#!/usr/bin/env python3
"""
Slime mold vs. India
====================
A Physarum-style adaptive network model (Tero et al., Science 327:439, 2010)
grown over a map of India. 16 major cities act as "food sources". The network
starts as a uniform mesh, keeps only routes that carry flow, and is then compared
with major trunk corridors. Finally a region is blocked and the network rewires.

Run:
    pip install numpy scipy matplotlib
    # ffmpeg must be installed and on PATH
    python physarum_india.py              # full render (~22 s video, a few minutes)
    python physarum_india.py --quick      # fast low-frame test render

Outputs (in ./out): slime_india.mp4, slime_vs_schematic.png, slime_rewired.png, metrics.json

Notes / honesty:
  * The India outline is a hand-built approximation, not survey-grade.
  * "Schematic comparison corridors" are SIMPLIFIED straight city-to-city links
    (Golden Quadrilateral + major N-S / E-W routes). They are not actual rail/road data.
  * Cost zones (Himalaya, Thar, NE hills, Rann of Kutch) are rough Gaussian/sigmoid fields.
"""
import argparse
import json
import math
import os
import subprocess
import time

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Circle
from matplotlib.path import Path
from scipy.sparse import coo_matrix, diags
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.sparse.linalg import splu
from scipy.spatial import cKDTree

# ----------------------------------------------------------------------------
# Parameters
# ----------------------------------------------------------------------------
SEED = 7
H = 25.0            # lattice spacing (km)
GAMMA = 1.6         # flux nonlinearity in f(Q) = Q^g / (1 + Q^g)
DT = 0.2            # adaptation step
K_PAIRS = 12        # random source/sink city pairs per iteration
D_FLOOR = 1e-5      # minimum conductivity of a live edge
I0 = 5.0            # source/sink current per city pair
DRAW_MIN = 0.03     # do not draw edges thinner than this (relative to thickest tube)
REL_THR = 0.15      # an edge counts as part of the "network" above this fraction of the thickest tube
TOL_KM = 50.0       # corridor/tube overlap tolerance
BLOCK_R = 150.0     # radius of the blocked zone (km)
T_GROW = 450
T_REPAIR = 250

DPI = 150
W, HPX = 1080, 1350
FPS = 30

BG = "#070a0f"
LAND = "#0e151e"
LAND_EDGE = "#26384a"
TXT = "#eef2f6"
MUTED = "#8ea0b2"
ACCENT = "#ffb02e"
RED = (1.0, 0.30, 0.30)

CMAP = LinearSegmentedColormap.from_list(
    "slime", ["#5c2a06", "#b8560b", "#ff9d1c", "#ffd24a", "#fff6cf"]
)

# ----------------------------------------------------------------------------
# Geography (approximate)
# ----------------------------------------------------------------------------
LON0, LAT0 = 83.0, 21.5
KM = 111.2
COSL = math.cos(math.radians(22.0))


def proj(lon, lat):
    lon = np.asarray(lon, dtype=float)
    lat = np.asarray(lat, dtype=float)
    return (lon - LON0) * KM * COSL, (lat - LAT0) * KM


def unproj(x, y):
    return LON0 + np.asarray(x) / (KM * COSL), LAT0 + np.asarray(y) / KM


# Rough outline of India (lon, lat), counter-clockwise from NW Gujarat.
INDIA = [
    (68.20, 23.75), (68.60, 23.15), (69.70, 22.75), (70.30, 22.95), (70.05, 22.45),
    (69.10, 22.35), (69.20, 22.00), (69.65, 21.65), (70.40, 20.90), (71.20, 20.75),
    (72.20, 21.10), (72.15, 21.80), (72.55, 22.30), (72.75, 21.70), (72.75, 21.10),
    (72.80, 20.40), (72.82, 18.95), (73.28, 17.00), (73.80, 15.45), (74.10, 14.80),
    (74.85, 12.85), (75.35, 11.90), (75.75, 11.25), (76.22, 9.95), (76.55, 8.90),
    (76.90, 8.50), (77.55, 8.07), (78.15, 8.75), (79.30, 9.28), (79.85, 10.30),
    (79.85, 10.77), (79.85, 11.93), (80.30, 13.10), (80.30, 13.60), (80.15, 14.45),
    (80.10, 15.50), (81.20, 16.15), (82.30, 16.95), (83.30, 17.70), (84.00, 18.30),
    (84.90, 19.25), (85.85, 19.80), (86.70, 20.30), (87.05, 21.50), (87.55, 21.60),
    (88.10, 21.60), (88.70, 21.70), (89.00, 22.05), (88.95, 22.70), (88.65, 23.40),
    (88.30, 24.20), (88.05, 24.65), (88.15, 25.20), (88.30, 25.90), (88.45, 26.30),
    (88.85, 26.25), (89.75, 25.95), (90.50, 25.15), (91.90, 25.15), (92.30, 24.95),
    (92.10, 24.35), (91.65, 24.10), (91.40, 23.45), (91.60, 23.00), (91.95, 22.55),
    (92.30, 22.05), (92.60, 21.95), (93.15, 22.15), (93.10, 23.00), (93.35, 23.80),
    (94.15, 23.85), (94.60, 24.50), (94.75, 25.30), (95.15, 26.45), (95.80, 26.90),
    (96.30, 27.30), (97.00, 27.70), (97.35, 28.25), (96.60, 28.75), (96.10, 29.40),
    (94.90, 29.35), (94.30, 29.10), (93.20, 28.70), (92.10, 28.20), (91.70, 27.80),
    (91.65, 27.30), (91.60, 26.90), (90.50, 26.80), (89.40, 26.75), (89.00, 26.85),
    (88.95, 27.35), (88.90, 27.95), (88.60, 28.10), (88.10, 27.90), (88.00, 27.40),
    (88.15, 26.95), (88.15, 26.50), (87.50, 26.40), (86.70, 26.45), (86.00, 26.65),
    (85.20, 26.75), (84.40, 27.00), (83.50, 27.40), (82.70, 27.55), (81.70, 28.10),
    (80.90, 28.60), (80.20, 28.90), (80.05, 29.50), (80.20, 30.20), (79.90, 30.90),
    (79.00, 31.10), (78.70, 31.80), (78.80, 32.30), (79.20, 32.65), (79.50, 33.20),
    (80.20, 34.20), (79.60, 35.20), (78.40, 35.60), (77.30, 35.50), (76.50, 35.90),
    (75.90, 36.60), (75.00, 36.95), (74.30, 36.90), (73.00, 36.70), (72.70, 35.80),
    (73.40, 35.10), (73.80, 34.60), (74.15, 33.80), (74.30, 33.20), (74.65, 32.80),
    (74.75, 31.90), (74.50, 31.60), (74.50, 30.95), (74.00, 30.35), (73.90, 29.90),
    (72.90, 28.70), (72.30, 27.90), (70.70, 27.00), (70.10, 26.20), (70.00, 25.40),
    (70.50, 24.70), (69.70, 24.35), (68.70, 23.95),
]

# name: (lon, lat, label offset in points, horizontal alignment)
CITIES = {
    "Delhi": (77.10, 28.61, (8, 4), "left"),
    "Chandigarh": (76.78, 30.73, (-8, 4), "right"),
    "Jaipur": (75.79, 26.91, (-8, 0), "right"),
    "Ahmedabad": (72.57, 23.02, (-8, 0), "right"),
    "Mumbai": (72.88, 19.08, (-8, 0), "right"),
    "Bhopal": (77.41, 23.26, (-8, 5), "right"),
    "Nagpur": (79.09, 21.15, (8, -3), "left"),
    "Hyderabad": (78.49, 17.39, (8, 0), "left"),
    "Bengaluru": (77.59, 12.97, (-8, -3), "right"),
    "Chennai": (80.27, 13.08, (8, -3), "left"),
    "Kochi": (76.27, 9.93, (-8, 0), "right"),
    "Lucknow": (80.95, 26.85, (8, 5), "left"),
    "Patna": (85.14, 25.59, (8, 3), "left"),
    "Kolkata": (88.36, 22.57, (8, -4), "left"),
    "Bhubaneswar": (85.83, 20.30, (8, -3), "left"),
    "Guwahati": (91.74, 26.14, (6, 9), "left"),
}

# Simplified trunk corridors (Golden Quadrilateral + major N-S / E-W routes).
CORRIDORS = [
    ("Delhi", "Jaipur"), ("Jaipur", "Ahmedabad"), ("Ahmedabad", "Mumbai"),
    ("Mumbai", "Bengaluru"), ("Bengaluru", "Chennai"),
    ("Chennai", "Bhubaneswar"), ("Bhubaneswar", "Kolkata"),
    ("Kolkata", "Patna"), ("Patna", "Lucknow"), ("Lucknow", "Delhi"),
    ("Delhi", "Bhopal"), ("Bhopal", "Nagpur"), ("Nagpur", "Hyderabad"),
    ("Hyderabad", "Bengaluru"), ("Bengaluru", "Kochi"),
    ("Delhi", "Chandigarh"), ("Kolkata", "Guwahati"), ("Patna", "Guwahati"),
    ("Bhopal", "Mumbai"), ("Nagpur", "Kolkata"), ("Hyderabad", "Chennai"),
    ("Lucknow", "Bhopal"),
]

HIM_LON = np.array([72, 75, 77, 79, 82, 85, 88, 91, 94, 98], dtype=float)
HIM_LAT = np.array([33.6, 32.3, 31.2, 30.5, 29.3, 28.0, 27.1, 27.0, 27.4, 28.0])


def blob(lon, lat, lon0, lat0, a, b):
    return np.exp(-(((lon - lon0) / a) ** 2 + ((lat - lat0) / b) ** 2))


def cost_field(lon, lat):
    """Travel-cost multiplier per node (1 = easy terrain)."""
    c = np.ones_like(lon)
    flat = np.interp(lon, HIM_LON, HIM_LAT)
    c = np.maximum(c, 1.0 + 5.0 / (1.0 + np.exp(-(lat - flat) / 0.45)))      # Himalaya
    c = np.maximum(c, 1.0 + 0.9 * blob(lon, lat, 71.3, 27.0, 2.4, 1.9))      # Thar desert
    c = np.maximum(c, 1.0 + 1.1 * blob(lon, lat, 93.8, 24.8, 2.6, 2.4))      # NE hills
    c = np.maximum(c, 1.0 + 1.0 * blob(lon, lat, 69.8, 23.8, 1.0, 0.6))      # Rann of Kutch
    return c


# ----------------------------------------------------------------------------
# Geometry / graph construction
# ----------------------------------------------------------------------------
def build_geometry():
    poly = np.array(INDIA)
    x0 = proj(66.5, 0)[0]
    x1 = proj(99.0, 0)[0]
    y0 = proj(0, 6.0)[1]
    y1 = proj(0, 38.0)[1]
    dy = H * math.sqrt(3) / 2
    rows = int((y1 - y0) / dy) + 1
    cols = int((x1 - x0) / H) + 1
    r, c = np.meshgrid(np.arange(rows), np.arange(cols), indexing="ij")
    X = x0 + c * H + (r % 2) * H / 2
    Y = y0 + r * dy
    pts = np.c_[X.ravel(), Y.ravel()]
    lon, lat = unproj(pts[:, 0], pts[:, 1])
    inside = Path(poly).contains_points(np.c_[lon, lat])
    pts = pts[inside]

    tree = cKDTree(pts)
    pairs = tree.query_pairs(r=1.74 * H, output_type="ndarray")  # 12-neighbourhood
    n = len(pts)
    g = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    big = np.argmax(np.bincount(lab))
    keep = lab == big
    remap = -np.ones(n, dtype=int)
    remap[keep] = np.arange(keep.sum())
    pts = pts[keep]
    pairs = remap[pairs]
    pairs = pairs[(pairs >= 0).all(axis=1)]
    I, J = pairs[:, 0], pairs[:, 1]

    lon, lat = unproj(pts[:, 0], pts[:, 1])
    cn = cost_field(lon, lat)
    Lphys = np.linalg.norm(pts[I] - pts[J], axis=1)
    Lcost = Lphys * (cn[I] + cn[J]) / 2.0

    names = list(CITIES)
    cll = np.array([[CITIES[k][0], CITIES[k][1]] for k in names])
    cx, cy = proj(cll[:, 0], cll[:, 1])
    city_xy = np.c_[cx, cy]
    tree = cKDTree(pts)
    _, city_node = tree.query(city_xy)
    assert len(set(city_node.tolist())) == len(names), "two cities snapped to one node"

    px, py = proj(poly[:, 0], poly[:, 1])
    return dict(
        pts=pts, I=I, J=J, Lphys=Lphys, Lcost=Lcost, names=names, city_xy=city_xy,
        city_node=city_node, poly_xy=np.c_[px, py],
        xlim=(px.min() - 60, px.max() + 60), ylim=(py.min() - 60, py.max() + 60),
    )


# ----------------------------------------------------------------------------
# Physarum dynamics (Tero et al. 2010)
# ----------------------------------------------------------------------------
class Slime:
    def __init__(self, geo, seed):
        self.pts, self.I, self.J = geo["pts"], geo["I"], geo["J"]
        self.L = geo["Lcost"]
        self.city_node = geo["city_node"]
        self.n = len(self.pts)
        self.alive = np.ones(len(self.I), dtype=bool)
        self.D = np.ones(len(self.I))
        self.rng = np.random.default_rng(seed)
        self.active = np.arange(len(self.city_node))

    def step(self):
        n, I, J = self.n, self.I, self.J
        C = np.where(self.alive, self.D / self.L, 0.0)
        A = coo_matrix((np.r_[C, C], (np.r_[I, J], np.r_[J, I])), shape=(n, n)).tocsr()
        deg = np.asarray(A.sum(axis=1)).ravel()
        eps = 1e-9 * max(deg.max(), 1e-12)
        lap = (diags(deg + eps) - A).tocsc()

        a, m = self.active, len(self.active)
        si = self.rng.integers(0, m, K_PAIRS)
        ti = (si + self.rng.integers(1, m, K_PAIRS)) % m
        B = np.zeros((n, K_PAIRS))
        B[self.city_node[a[si]], np.arange(K_PAIRS)] += I0
        B[self.city_node[a[ti]], np.arange(K_PAIRS)] -= I0
        P = splu(lap).solve(B)

        Q = np.abs(C[:, None] * (P[I] - P[J])).mean(axis=1)
        f = Q ** GAMMA / (1.0 + Q ** GAMMA)
        self.D = np.maximum(self.D + DT * (f - self.D), D_FLOOR)
        self.D[~self.alive] = 0.0

    def block(self, center, radius):
        inside = np.linalg.norm(self.pts - center, axis=1) < radius
        self.alive &= ~(inside[self.I] | inside[self.J])
        self.D[~self.alive] = 0.0


def choose_block(slime, city_xy, radius):
    """Pick the busiest interior spot, far from any city, that keeps all cities connected."""
    pts, I, J = slime.pts, slime.I, slime.J
    mid = (pts[I] + pts[J]) / 2
    order = np.argsort(-slime.D)
    for e in order[:4000]:
        c = mid[e]
        if np.min(np.linalg.norm(city_xy - c, axis=1)) < radius + 80:
            continue
        inside = np.linalg.norm(pts - c, axis=1) < radius
        keep = slime.alive & ~(inside[I] | inside[J])
        g = coo_matrix((np.ones(keep.sum()), (I[keep], J[keep])), shape=(slime.n, slime.n))
        _, lab = connected_components(g, directed=False)
        if len(set(lab[slime.city_node].tolist())) == 1:
            return c
    raise RuntimeError("no valid block location found")


# ----------------------------------------------------------------------------
# Metrics
# ----------------------------------------------------------------------------
def net_mask(D, alive):
    """Edges that count as part of the network (relative to the thickest tube)."""
    return alive & (D > REL_THR * D[alive].max())


def analyse(geo, D, alive):
    pts, I, J, node = geo["pts"], geo["I"], geo["J"], geo["city_node"]
    n = len(pts)
    m = net_mask(D, alive)
    w = np.linalg.norm(pts[I[m]] - pts[J[m]], axis=1)
    g = coo_matrix((w, (I[m], J[m])), shape=(n, n)).tocsr()
    dist = dijkstra(g, directed=False, indices=node)[:, node]
    cxy = pts[node]
    straight = np.linalg.norm(cxy[:, None] - cxy[None], axis=2)
    iu = np.triu_indices(len(node), 1)
    d, s = dist[iu], straight[iu]
    ok = np.isfinite(d)
    return dict(
        total_km=float(w.sum()),
        detour=float((d[ok] / s[ok]).mean()),
        connected_pairs=int(ok.sum()),
        pairs=int(len(d)),
        mask=m,
    )


def schematic_segments(geo):
    idx = {k: i for i, k in enumerate(geo["names"])}
    return [(geo["city_xy"][idx[a]], geo["city_xy"][idx[b]]) for a, b in CORRIDORS]


def analyse_schematic(geo):
    segs = schematic_segments(geo)
    idx = {k: i for i, k in enumerate(geo["names"])}
    nc = len(geo["names"])
    rows, cols, ws = [], [], []
    for (a, b), (pa, pb) in zip(CORRIDORS, segs):
        rows.append(idx[a]); cols.append(idx[b]); ws.append(np.linalg.norm(pb - pa))
    g = coo_matrix((ws, (rows, cols)), shape=(nc, nc)).tocsr()
    dist = dijkstra(g, directed=False)
    cxy = geo["city_xy"]
    straight = np.linalg.norm(cxy[:, None] - cxy[None], axis=2)
    iu = np.triu_indices(nc, 1)
    d, s = dist[iu], straight[iu]
    ok = np.isfinite(d)
    return dict(total_km=float(np.sum(ws)), detour=float((d[ok] / s[ok]).mean()),
                connected_pairs=int(ok.sum()), pairs=int(len(d)))


def coverage(geo, mask, tol=TOL_KM):
    pts, I, J = geo["pts"], geo["I"], geo["J"]
    segs = schematic_segments(geo)
    tube_nodes = np.unique(np.r_[I[mask], J[mask]])
    tt = cKDTree(pts[tube_nodes])
    samples = []
    for a, b in segs:
        L = np.linalg.norm(b - a)
        k = max(int(L / 5), 2)
        t = np.linspace(0, 1, k)[:, None]
        samples.append(a + t * (b - a))
    d, _ = tt.query(np.vstack(samples))
    real_covered = float((d <= tol).mean())

    mids = (pts[I[mask]] + pts[J[mask]]) / 2
    dmin = np.full(len(mids), np.inf)
    for a, b in segs:
        ab = b - a
        t = np.clip(((mids - a) @ ab) / (ab @ ab), 0, 1)
        dmin = np.minimum(dmin, np.linalg.norm(mids - (a + t[:, None] * ab), axis=1))
    slime_covered = float((dmin <= tol).mean())
    return real_covered, slime_covered


# ----------------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------------
class Scene:
    def __init__(self, geo):
        self.geo = geo
        self.seg = np.stack([geo["pts"][geo["I"]], geo["pts"][geo["J"]]], axis=1)
        self.fig = plt.figure(figsize=(W / DPI, HPX / DPI), dpi=DPI, facecolor=BG)
        self.ax = ax = self.fig.add_axes([0.03, 0.115, 0.94, 0.755])
        ax.set_facecolor(BG)
        ax.axis("off")
        ax.set_xlim(*geo["xlim"])
        ax.set_ylim(*geo["ylim"])
        ax.set_aspect("equal", adjustable="box")
        px, py = geo["poly_xy"].T
        ax.fill(px, py, fc=LAND, ec=LAND_EDGE, lw=1.0, zorder=1)

        halo = [pe.withStroke(linewidth=2.6, foreground=BG)]
        cxy = geo["city_xy"]
        ax.scatter(cxy[:, 0], cxy[:, 1], s=26, c="white", edgecolors=BG, linewidths=0.8, zorder=7)
        for name, (x, y) in zip(geo["names"], cxy):
            _, _, off, ha = CITIES[name]
            ax.annotate(name, (x, y), xytext=off, textcoords="offset points", ha=ha, va="center",
                        fontsize=8.6, color=TXT, zorder=8, path_effects=halo)

        # real corridors overlay
        rs = schematic_segments(geo)
        self.real_lc = LineCollection(rs, colors="white", linewidths=1.7,
                                      linestyles=(0, (4, 3)), zorder=5.5)
        self.real_lc.set_visible(False)
        ax.add_collection(self.real_lc)

        # blocked zone
        self.circle = Circle((0, 0), BLOCK_R, zorder=2.5)
        self.circle.set_visible(False)
        ax.add_patch(self.circle)
        self.circle_label = ax.text(0, 0, "Blocked zone", color=(1, 0.55, 0.55), fontsize=9,
                                    ha="center", va="center", zorder=9, visible=False,
                                    path_effects=halo)

        handles = [Line2D([0], [0], color="#ffb02e", lw=3.2),
                   Line2D([0], [0], color="white", lw=1.7, ls=(0, (4, 3)))]
        self.legend = ax.legend(handles, ["Slime-mold network", "Illustrative city links (not tracks)"],
                                loc="lower right", bbox_to_anchor=(0.985, 0.205), frameon=True,
                                facecolor="#0b1118", edgecolor="#2a3b4e", labelcolor=TXT,
                                fontsize=8.2, framealpha=0.92)
        self.legend.set_zorder(10)
        self.legend.set_visible(False)

        self.box = ax.text(0.985, 0.012, "", transform=ax.transAxes, ha="right", va="bottom",
                           family="monospace", fontsize=8.0, color=TXT, zorder=10, visible=False,
                           bbox=dict(boxstyle="round,pad=0.55", fc="#0b1118", ec="#2a3b4e", alpha=0.93))

        f = self.fig
        f.text(0.5, 0.953, "Slime mold vs. India", ha="center", va="center", color=TXT,
               fontsize=27, fontweight="bold")
        f.text(0.5, 0.922, "Can Physarum-inspired flow rules connect 16 Indian cities?",
               ha="center", va="center", color=MUTED, fontsize=10.2)
        self.step_txt = f.text(0.5, 0.893, "", ha="center", va="center", color=ACCENT,
                               fontsize=13, fontweight="bold")
        f.text(0.5, 0.050, "Model: Tero et al., Science 327 (2010)   |   Python, NumPy, SciPy",
               ha="center", va="center", color=MUTED, fontsize=8.6)
        f.text(0.5, 0.027, "Illustrative city-link sketch, not actual rail tracks or surveyed roads.",
               ha="center", va="center", color="#5d6e80", fontsize=7.6)
        self.dyn = []

    def draw(self, D, alive, label, overlay=0.0, box=None, block=0.0, block_center=None, dim=1.0):
        for a in self.dyn:
            a.remove()
        self.dyn = []
        Dn = D / max(D[alive].max(), 1e-9)          # normalise so the thickest tube = 1
        idx = np.nonzero(alive & (Dn > DRAW_MIN))[0]
        idx = idx[np.argsort(Dn[idx])]
        d = Dn[idx]
        segs = self.seg[idx]
        cols = CMAP(np.clip(d, 0, 1) ** 0.45 * dim)
        cols[:, 3] = np.clip(0.20 + 0.85 * d ** 0.5, 0, 1)
        lw = 0.2 + 3.2 * d ** 0.9
        gcols = cols.copy()
        gcols[:, 3] *= 0.16
        glow = LineCollection(segs, linewidths=lw * 2.8, colors=gcols, zorder=3, capstyle="round")
        core = LineCollection(segs, linewidths=lw, colors=cols, zorder=4, capstyle="round")
        self.ax.add_collection(glow)
        self.ax.add_collection(core)
        self.dyn = [glow, core]

        self.step_txt.set_text(label)

        self.real_lc.set_visible(overlay > 0)
        self.real_lc.set_alpha(overlay)

        if block > 0 and block_center is not None:
            self.circle.set_center(tuple(block_center))
            self.circle.set_facecolor((*RED, 0.20 * block))
            self.circle.set_edgecolor((*RED, 0.90 * block))
            self.circle.set_linewidth(1.6)
            self.circle.set_visible(True)
            self.circle_label.set_position((block_center[0], block_center[1] + BLOCK_R + 55))
            self.circle_label.set_alpha(block)
            self.circle_label.set_visible(True)
        else:
            self.circle.set_visible(False)
            self.circle_label.set_visible(False)

        if box:
            self.box.set_text(box["text"])
            self.box.set_alpha(box.get("alpha", 1.0))
            self.box.set_visible(True)
            self.legend.set_visible(box.get("legend", False))
        else:
            self.box.set_visible(False)
            self.legend.set_visible(False)

    def grab(self):
        self.fig.canvas.draw()
        return np.asarray(self.fig.canvas.buffer_rgba()).tobytes()

    def save_png(self, path):
        self.fig.savefig(path, dpi=DPI, facecolor=BG)


def eased_steps(total, n_frames, power=1.8):
    t = np.linspace(0, 1, n_frames) ** power
    return np.unique(np.round(t * total).astype(int))


def fmt_km(x):
    return f"{x / 1000:5.1f}k km"


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="fast low-frame test render")
    ap.add_argument("--out", default="out")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    t0 = time.time()

    def log(msg):
        print(f"[{time.time() - t0:6.1f}s] {msg}", flush=True)

    if args.quick:
        t_grow, t_rep = 140, 70
        FR = dict(intro=6, grow=30, hold1=3, fade_in=6, compare=12, fade_out=4, block_in=6,
                  repair=18, final=12)
    else:
        t_grow, t_rep = T_GROW, T_REPAIR
        FR = dict(intro=36, grow=240, hold1=15, fade_in=36, compare=90, fade_out=20, block_in=24,
                  repair=130, final=75)

    geo = build_geometry()
    log(f"grid: {len(geo['pts'])} nodes, {len(geo['I'])} edges, {len(geo['names'])} cities")

    slime = Slime(geo, args.seed)

    # ---- simulate phase 1 (growth) -----------------------------------------
    grow_idx = set(eased_steps(t_grow, FR["grow"]).tolist())
    snaps_grow = [slime.D.copy().astype(np.float32)]
    for step in range(1, t_grow + 1):
        slime.step()
        if step in grow_idx:
            snaps_grow.append(slime.D.astype(np.float32).copy())
    D_grown = slime.D.copy()
    log(f"growth done ({t_grow} iterations), network edges: {net_mask(D_grown, slime.alive).sum()}")

    before = analyse(geo, D_grown, slime.alive)
    real = analyse_schematic(geo)
    real_cov, slime_cov = coverage(geo, before["mask"])
    log(f"slime: {before['total_km']:.0f} km, detour {before['detour']:.3f} | "
        f"sketch: {real['total_km']:.0f} km, detour {real['detour']:.3f} | "
        f"coverage real->slime {real_cov:.0%}, slime->real {slime_cov:.0%}")

    # ---- block + repair -------------------------------------------------------
    center = choose_block(slime, geo["city_xy"], BLOCK_R)
    slime.block(center, BLOCK_R)
    immediate = analyse(geo, slime.D, slime.alive)
    log(f"immediate loss: {immediate['connected_pairs']}/{immediate['pairs']} connected under the {REL_THR:.0%} threshold")
    rep_idx = set(eased_steps(t_rep, FR["repair"]).tolist())
    snaps_rep = [slime.D.astype(np.float32).copy()]
    alive_after = slime.alive.copy()
    for step in range(1, t_rep + 1):
        slime.step()
        if step in rep_idx:
            snaps_rep.append(slime.D.astype(np.float32).copy())
    D_repaired = slime.D.copy()
    after = analyse(geo, D_repaired, slime.alive)
    log(f"after block: {after['total_km']:.0f} km, detour {after['detour']:.3f}, "
        f"connected pairs {after['connected_pairs']}/{after['pairs']}")

    # ---- text for overlays -----------------------------------------------------
    compare_text = (
        f"{'':17}{'Slime mold':>11}{'Sketch*':>10}\n"
        f"{'Total length':17}{fmt_km(before['total_km']):>11}{fmt_km(real['total_km']):>10}\n"
        f"{'Avg route detour':17}{before['detour']:>10.2f}x{real['detour']:>9.2f}x\n"
        f"{'':17}{'':>11}{'':>10}\n"
        f"Sketch links within {TOL_KM:.0f} km of a tube: {real_cov:.0%}\n"
        f"Slime tubes near schematic links ({TOL_KM:.0f} km): {slime_cov:.0%}\n"
        f"*hand-selected straight city links"
    )
    rewired_text = (
        f"Blocked zone radius       {BLOCK_R:.0f} km\n"
        f"Connected immediately      {immediate['connected_pairs']}/{immediate['pairs']}\n"
        f"Connected after adapting   {after['connected_pairs']}/{after['pairs']}\n"
        f"Avg route detour          {before['detour']:.2f}x -> {after['detour']:.2f}x\n"
        f"Total network length      {before['total_km'] / 1000:.1f}k -> {after['total_km'] / 1000:.1f}k km\n"
        f"Global flow solve; each tube adapts from its own flux."
    )

    # ---- render -------------------------------------------------------------------
    scene = Scene(geo)
    vid = os.path.join(args.out, "slime_india.mp4")
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
         "-s", f"{W}x{HPX}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", vid],
        stdin=subprocess.PIPE,
    )
    nframes = 0

    def emit(*a, **k):
        nonlocal nframes
        scene.draw(*a, **k)
        data = scene.grab()
        ff.stdin.write(data)
        nframes += 1
        return data

    def hold(data, n):
        nonlocal nframes
        for _ in range(n):
            ff.stdin.write(data)
            nframes += 1

    alive_all = np.ones(len(geo["I"]), dtype=bool)
    L1 = "Step 1  |  Start: all candidate connections are available"
    L2 = "Step 1  |  It keeps only the routes that carry flow"
    L3 = "Step 2  |  Compare with schematic city links"
    L4 = "Step 3  |  Block a major route and watch it rewire"

    # intro hold
    DIM0 = 0.45   # the opening mold is a dim amber; it brightens as veins emerge
    data = emit(snaps_grow[0].astype(float), alive_all, L1, dim=DIM0)
    hold(data, FR["intro"])
    log("rendering growth")
    ng = max(len(snaps_grow) - 1, 1)
    for i, D in enumerate(snaps_grow[1:]):
        dim = DIM0 + (1 - DIM0) * min(1.0, i / (0.3 * ng))
        data = emit(D.astype(float), alive_all, L2, dim=dim)
    hold(data, FR["hold1"])

    # compare: fade overlay in, hold, fade out
    log("rendering comparison")
    for i in range(FR["fade_in"]):
        a = (i + 1) / FR["fade_in"]
        data = emit(D_grown, alive_all, L3, overlay=a,
                    box=dict(text=compare_text, alpha=a, legend=a > 0.5))
    cmp_png = os.path.join(args.out, "slime_vs_schematic.png")
    scene.save_png(cmp_png)
    hold(data, FR["compare"])
    for i in range(FR["fade_out"]):
        a = 1 - (i + 1) / FR["fade_out"]
        data = emit(D_grown, alive_all, L3, overlay=a,
                    box=dict(text=compare_text, alpha=max(a, 0.01), legend=a > 0.5))

    # block fade-in (network still intact)
    log("rendering disruption")
    for i in range(FR["block_in"]):
        a = (i + 1) / FR["block_in"]
        data = emit(D_grown, alive_all, L4, block=a, block_center=center)
    # repair
    for D in snaps_rep:
        data = emit(D.astype(float), alive_after, L4, block=1.0, block_center=center)
    data = emit(D_repaired, alive_after, L4, block=1.0, block_center=center,
                box=dict(text=rewired_text, alpha=1.0))
    rew_png = os.path.join(args.out, "slime_rewired.png")
    scene.save_png(rew_png)
    hold(data, FR["final"])

    ff.stdin.close()
    ff.wait()
    log(f"video written: {vid}  ({nframes} frames, {nframes / FPS:.1f} s)")

    metrics = dict(
        slime_before=dict(total_km=before["total_km"], detour=before["detour"],
                          connected_pairs=before["connected_pairs"], pairs=before["pairs"]),
        slime_immediately_after_block=dict(total_km=immediate["total_km"], detour=immediate["detour"],
                                           connected_pairs=immediate["connected_pairs"], pairs=immediate["pairs"]),
        slime_after_adaptation=dict(total_km=after["total_km"], detour=after["detour"],
                                    connected_pairs=after["connected_pairs"], pairs=after["pairs"]),
        schematic_corridors=real,
        schematic_links_near_tubes=real_cov,
        fraction_of_tube_edges_near_schematic_links=slime_cov,
        tolerance_km=TOL_KM, seed=args.seed, gamma=GAMMA,
        iterations=dict(growth=t_grow, repair=t_rep),
    )
    with open(os.path.join(args.out, "metrics.json"), "w") as fh:
        json.dump(metrics, fh, indent=2)
    log("done")


if __name__ == "__main__":
    main()
