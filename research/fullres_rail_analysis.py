"""Full-resolution comparison with mapped railway LINE geometry (v4.2 repaired).

Replaces the coarse 0.2-degree raster check from v4. Two questions, same data:

1. PROXIMITY  - how much of each network's length lies within r km of a mapped railway line?
2. TOPOLOGY   - if we stitch the railway lines into a graph, how long are real rail routes between
                the 16 cities compared with the straight-line distance (the same 'detour' the model reports)?

Source file (download first):  python research/download_real_tracks.py   -> data/INDIAN_RAILWAYS.geojson
Run:                           python research/fullres_rail_analysis.py
Outputs:                       out/fullres_rail_analysis.json, data/rail_lines_simplified.npz

All distances are planar kilometres in an azimuthal-equidistant projection centred on 22N, 82E
(projection distortion varies across India; these are not geodesic lengths). Railway kilometres count parallel/duplicate tracks and are NOT
Indian Railways route-km.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from pyproj import CRS, Transformer
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.network_artifacts import load_masks, load_mask
import physarum_india as p  # noqa: E402

AEQD = CRS.from_proj4("+proj=aeqd +lat_0=22 +lon_0=82 +datum=WGS84 +units=m +no_defs")
TO_M = Transformer.from_crs("EPSG:4326", AEQD, always_xy=True)
TOLERANCES_KM = (5, 10, 25, 50)
STITCH_KM = 0.6
INDIA_BOX = (66.0, 99.0, 6.0, 38.0)  # lon_min, lon_max, lat_min, lat_max


EXPECTED_SOURCE_GIT_SHA = "63ff14b3f3b62a6d18d4950e9ab4ba99a3c5c16d"


def verify_source(path):
    buf = Path(path).read_bytes()
    actual = hashlib.sha1(f"blob {len(buf)}\0".encode() + buf).hexdigest()
    if actual != EXPECTED_SOURCE_GIT_SHA:
        raise ValueError(f"Rail source hash mismatch: {actual}")
    return actual


def load_lines(path):
    """LineString coordinate arrays (lon, lat) from a GeoJSON file, skipping bad / out-of-India lines."""
    with open(path, encoding="utf-8") as fh:
        feats = json.load(fh)["features"]
    lines = []
    for f in feats:
        g = f.get("geometry") or {}
        if g.get("type") != "LineString":
            continue
        a = np.asarray(g["coordinates"], float)
        if a.ndim != 2 or len(a) < 2 or a.shape[1] < 2 or not np.isfinite(a[:, :2]).all():
            continue
        a = a[:, :2]
        x0, x1, y0, y1 = INDIA_BOX
        if not ((a[:, 0] >= x0) & (a[:, 0] <= x1) & (a[:, 1] >= y0) & (a[:, 1] <= y1)).all():
            continue
        lines.append(a)
    return lines, len(feats)


def lines_to_km(lines):
    """Flatten lines to one vertex array (km). Returns vertices, line start offsets, line lengths (vertex counts)."""
    lens = np.array([len(a) for a in lines])
    start = np.r_[0, np.cumsum(lens)[:-1]]
    ll = np.vstack(lines)
    x, y = TO_M.transform(ll[:, 0], ll[:, 1])
    return np.c_[x, y] / 1000.0, start, lens


def segment_indices(start, lens):
    a = np.concatenate([np.arange(s, s + n - 1) for s, n in zip(start, lens)])
    return a, a + 1


def assert_physical_tracks(V, start, lens, max_km=100.0):
    """Refuse train-stop route data: its straight chords between stations are not physical track.

    The real railway GIS used here has a longest vertex-to-vertex segment of about 10 km.
    """
    a, b = segment_indices(start, lens)
    longest = float(np.linalg.norm(V[a] - V[b], axis=1).max())
    if longest > max_km:
        raise ValueError(f"Segment of {longest:.0f} km found: this looks like a train-stop route, NOT physical track geometry")
    return longest


def sample_segments(P, A, B, step=3.0):
    """Points at <= step km spacing along segments P[A]->P[B], each carrying the km it represents."""
    L = np.linalg.norm(P[A] - P[B], axis=1)
    k = np.maximum(np.ceil(L / step).astype(int), 1)
    rep = np.repeat(np.arange(len(A)), k)
    t = (np.arange(k.sum()) - np.repeat(np.cumsum(k) - k, k) + 0.5) / np.repeat(k, k)
    return P[A][rep] + (P[B][rep] - P[A][rep]) * t[:, None], (L / k)[rep]


def rail_topology(V, start, lens, city_km, stitch_km=STITCH_KM):
    """Stitch rail lines into a graph and measure route distance / straight-line distance between cities.

    Line ends are joined to any rail vertex within stitch_km (junction tolerance). Cities snap to the
    nearest rail vertex. Detour = shortest rail path / straight-line distance, averaged over city pairs.
    """
    N = len(V)
    sa, sb = segment_indices(start, lens)
    sw = np.linalg.norm(V[sa] - V[sb], axis=1)
    tree = cKDTree(V)
    ends = np.r_[start, start + lens - 1]
    extra = [(i, j) for i, nb in zip(ends, tree.query_ball_point(V[ends], stitch_km)) for j in nb if j != i]
    extra = np.array(extra, int).reshape(-1, 2)
    ea = np.r_[sa, extra[:, 0]]
    eb = np.r_[sb, extra[:, 1]]
    ew = np.r_[sw, np.linalg.norm(V[extra[:, 0]] - V[extra[:, 1]], axis=1)]
    low, high = np.minimum(ea, eb), np.maximum(ea, eb)
    order = np.lexsort((ew, high, low))
    low, high, ew = low[order], high[order], ew[order]
    first = np.r_[True, (low[1:] != low[:-1]) | (high[1:] != high[:-1])]
    low, high, ew = low[first], high[first], ew[first]
    G = coo_matrix((np.r_[ew, ew], (np.r_[low, high], np.r_[high, low])), shape=(N, N)).tocsr()
    ncomp, lab = connected_components(G, directed=False)
    snap_d, snap_i = tree.query(city_km)
    D = dijkstra(G, directed=False, indices=snap_i)[:, snap_i]
    # Include terminal-to-vertex access legs, on common lattice terminal coordinates.
    D = D + snap_d[:, None] + snap_d[None, :]
    straight = np.linalg.norm(city_km[:, None] - city_km[None], axis=2)
    iu = np.triu_indices(len(city_km), 1)
    ok = np.isfinite(D[iu])
    detour = D[iu][ok] / straight[iu][ok]
    sizes = np.bincount(lab)
    return dict(
        stitch_km=stitch_km, components=int(ncomp), largest_component_share=float(sizes.max() / N),
        pairs=int(len(ok)), pairs_connected=int(ok.sum()),
        mean_detour=float(detour.mean()) if ok.any() else float("nan"),
        median_detour=float(np.median(detour)) if ok.any() else float("nan"),
        p90_detour=float(np.quantile(detour, 0.9)) if ok.any() else float("nan"),
        max_snap_km=float(snap_d.max()),
    )


def model_samples(geo, mask, step=3.0):
    """Sample a model network (lattice edges where mask) in the same AEQD km frame."""
    P = geo["pts"]
    I, J = geo["I"][mask], geo["J"][mask]
    lon1, lat1 = p.unproj(P[I][:, 0], P[I][:, 1])
    lon2, lat2 = p.unproj(P[J][:, 0], P[J][:, 1])
    x1, y1 = TO_M.transform(lon1, lat1)
    x2, y2 = TO_M.transform(lon2, lat2)
    A, B = np.c_[x1, y1] / 1000.0, np.c_[x2, y2] / 1000.0
    n = len(A)
    return sample_segments(np.vstack([A, B]), np.arange(n), np.arange(n) + n, step)


def proximity(rail_pts, rail_w, geo, mask, tolerances=TOLERANCES_KM):
    pts, w = model_samples(geo, mask)
    d, _ = cKDTree(rail_pts).query(pts)
    d_rev, _ = cKDTree(pts).query(rail_pts)
    return dict(
        model_km=float(w.sum()), median_dist_km=float(np.median(d)),
        model_length_within={str(t): float(w[d <= t].sum() / w.sum()) for t in tolerances},
        rail_length_within_model={str(t): float(rail_w[d_rev <= t].sum() / rail_w.sum()) for t in tolerances},
    )


def save_simplified(lines, path, tol_deg=0.01):
    """Compact copy of the rail lines for drawing (Douglas-Peucker, ~1 km). Requires shapely."""
    import shapely
    coords, offsets = [], [0]
    for a in lines:
        s = np.asarray(shapely.simplify(shapely.LineString(a), tol_deg).coords, np.float32)
        coords.append(s)
        offsets.append(offsets[-1] + len(s))
    np.savez_compressed(path, coords=np.vstack(coords), offsets=np.asarray(offsets, np.int64))
    return offsets[-1]


def load_simplified(path):
    z = np.load(path)
    c, o = z["coords"], z["offsets"]
    return [c[o[i]:o[i + 1]] for i in range(len(o) - 1)]


def network_masks(out_dir, geo=None):
    if geo is None:
        geo = p.build_geometry()
    bm = load_masks(out_dir / "baseline_masks.npz", geo)
    return {
        "Physarum": bm["Physarum"],
        "Terminal MST": bm["terminal_MST_expanded"],
        "Delhi shortest-path union": bm["Delhi_shortest_path_union"],
        "Augmented MST": load_mask(out_dir / "augmented_mst_mask.npy", geo),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tracks", default=str(ROOT / "data" / "INDIAN_RAILWAYS.geojson"))
    ap.add_argument("--out", default=str(ROOT / "out" / "fullres_rail_analysis.json"))
    ap.add_argument("--simplified", default=str(ROOT / "data" / "rail_lines_simplified.npz"))
    ap.add_argument("--no-simplified", action="store_true")
    args = ap.parse_args()

    verify_source(args.tracks)
    lines, n_feats = load_lines(args.tracks)
    V, start, lens = lines_to_km(lines)
    assert_physical_tracks(V, start, lens)
    sa, sb = segment_indices(start, lens)
    rail_pts, rail_w = sample_segments(V, sa, sb)
    print(f"{len(lines)} of {n_feats} features used; {len(V)} vertices; polyline total {rail_w.sum():.0f} km")

    geo = p.build_geometry()
    prox = {name: proximity(rail_pts, rail_w, geo, m) for name, m in network_masks(ROOT / "out").items()}
    for name, r in prox.items():
        print(f"{name:28s}", "  ".join(f"{t}km {r['model_length_within'][str(t)]:.1%}" for t in TOLERANCES_KM))

    clon, clat = p.unproj(geo["pts"][geo["city_node"], 0], geo["pts"][geo["city_node"], 1])
    cx, cy = TO_M.transform(clon, clat)
    city_km = np.c_[cx, cy] / 1000.0
    topo = rail_topology(V, start, lens, city_km)
    sens = {str(s): rail_topology(V, start, lens, city_km, s)["mean_detour"] for s in (0.1, 0.3, 1.5)}
    print(f"real rail topology: {topo['pairs_connected']}/{topo['pairs']} pairs, mean detour {topo['mean_detour']:.3f} "
          f"(stitch tolerance sensitivity: {sens})")

    result = dict(
        source="datta07/INDIAN-SHAPEFILES INDIA/INDIAN_RAILWAYS.geojson (git blob 63ff14b3f3b62a6d18d4950e9ab4ba99a3c5c16d)",
        features_used=len(lines), features_total=n_feats, vertices=int(len(V)),
        polyline_km=float(rail_w.sum()), tolerances_km=list(TOLERANCES_KM),
        proximity=prox, rail_topology=topo, rail_detour_vs_stitch_tolerance_km=sens,
        notes="Common lattice-snapped terminals; rail access legs included. Undirected links deduplicated by minimum length. Planar AEQD km. Rail km counts parallel/duplicate tracks. Proximity is not topology; "
              "mean_detour for rail is for the ENTIRE mapped network, which has far more track than the 16-city models.",
    )
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2))
    print("wrote", args.out)
    if not args.no_simplified:
        n = save_simplified(lines, args.simplified)
        print(f"wrote {args.simplified} ({n} vertices)")


if __name__ == "__main__":
    main()
