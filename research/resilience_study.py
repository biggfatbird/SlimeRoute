"""Resilience study (v4.2 repaired): one common, neutral set of blocked zones for every design.

Why: earlier damage tests used site sets drawn from the networks themselves (and different sets in
different scripts: 84% vs 92% for the same seed-7 network). Here the blocked zones are drawn
UNIFORMLY at random over the lattice (mainland India), independent of every network, then applied
identically to each design.

Protocol (static damage; no re-adaptation): remove every candidate edge touching a node within `radius`
km of the centre, then count the city pairs still connected through the network. Centres closer than
radius+35 km to a city are skipped (those trivially isolate the city for every design).

    python research/resilience_study.py            # ~4 min on 2 cores; writes out/resilience_study.json
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.network_artifacts import load_masks, load_mask
import physarum_india as p  # noqa: E402
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from research.network_artifacts import save_masks
from research.benchmark import baselines, blocked_mask, city_pair_mask, network_metrics  # noqa: E402

SEEDS = [1, 2, 3, 4, 5, 6, 7, 11, 21, 42]
RADII = (100, 150, 200)
SITES = 300
SITE_SEED = 20261101


def sample_sites(geo, radius, n=SITES, seed=SITE_SEED):
    """n blocked-zone centres drawn uniformly from lattice nodes that are >= radius+35 km from every city."""
    d = np.linalg.norm(geo["pts"][:, None, :] - geo["city_xy"][None, :, :], axis=2).min(axis=1)
    ok = np.where(d > radius + 35)[0]
    rng = np.random.default_rng(seed + radius)
    return geo["pts"][rng.choice(ok, size=n, replace=False)]


def survival(geo, mask, centers, radius):
    """Pairs still connected for each blocked zone (array of length len(centers))."""
    counts = []
    for c in centers:
        keep = mask & blocked_mask(geo, c, radius)
        graph = coo_matrix((np.ones(keep.sum()), (geo["I"][keep], geo["J"][keep])), shape=(len(geo["pts"]),) * 2).tocsr()
        _, labels = connected_components(graph, directed=False)
        groups = np.bincount(labels[geo["city_node"]])
        counts.append(int(np.sum(groups * (groups - 1) // 2)))
    return np.asarray(counts)


def grow(seed):
    geo = p.build_geometry()
    s = p.Slime(geo, seed)
    for _ in range(p.T_GROW):
        s.step()
    return seed, city_pair_mask(geo, s.D, s.alive, p.REL_THR)


def summarize(counts, total=120):
    return dict(sites=int(len(counts)), fraction_all_pairs_connected=float(np.mean(counts == total)),
                mean_pairs_connected=float(np.mean(counts)), min_pairs_connected=int(np.min(counts)), all_remaining_pairs=counts.tolist())


def main():
    geo = p.build_geometry()
    designs = {k: v for k, v in baselines(geo).items()}
    designs = {"Terminal MST": designs["terminal_MST_expanded"], "Delhi shortest-path union": designs["Delhi_shortest_path_union"],
               "Augmented MST": load_mask(ROOT / "out" / "augmented_mst_mask.npy", geo)}
    if "--reuse-masks" in sys.argv:
        cached = load_masks(ROOT / "out" / "physarum_seed_masks.npz", geo)
        physarum = {seed: cached[str(seed)] for seed in SEEDS}
    else:
        with Pool(2) as pool:
            rows = []
            for item in pool.imap_unordered(grow, SEEDS):
                rows.append(item)
                print(f"grown seed {item[0]}", flush=True)
        found = dict(rows)
        physarum = {seed: found[seed] for seed in SEEDS}
    save_masks(ROOT / "out" / "physarum_seed_masks.npz", geo, **{str(k): v for k, v in physarum.items()})
    print("grown", len(physarum), "Physarum networks", flush=True)

    out = dict(protocol=__doc__.split("Protocol")[1].split("python")[0].strip(), radii_km=list(RADII), sites_per_radius=SITES,
               site_seed=SITE_SEED, physarum_seeds=SEEDS, results={})
    for radius in RADII:
        centers = sample_sites(geo, radius)
        res = {}
        heuristic_counts = survival(geo, designs["Augmented MST"], centers, radius)
        for name, mask in designs.items():
            res[name] = dict(length_km=network_metrics(geo, mask)["length_km_approx"],
                             **summarize(survival(geo, mask, centers, radius)))
        per_seed = {sd: summarize(survival(geo, m, centers, radius)) for sd, m in physarum.items()}
        fr = np.array([v["fraction_all_pairs_connected"] for v in per_seed.values()])
        mp = np.array([v["mean_pairs_connected"] for v in per_seed.values()])
        res["Physarum (10 seeds)"] = dict(
            length_km=float(np.mean([network_metrics(geo, m)["length_km_approx"] for m in physarum.values()])),
            sites=SITES, fraction_all_pairs_connected=float(fr.mean()), fraction_sd_across_seeds=float(fr.std(ddof=1)),
            fraction_min_seed=float(fr.min()), fraction_max_seed=float(fr.max()),
            mean_pairs_connected=float(mp.mean()), per_seed={str(k): v for k, v in per_seed.items()})
        differences = np.array([(np.array(v["all_remaining_pairs"]) == 120).astype(float) - (heuristic_counts == 120).astype(float) for v in per_seed.values()])
        rng = np.random.default_rng(SITE_SEED + radius + 9000)
        means = np.empty(2000)
        for b in range(len(means)):
            means[b] = differences[rng.integers(0, len(SEEDS), len(SEEDS))][:, rng.integers(0, SITES, SITES)].mean()
        res["paired_comparison"] = dict(physarum_minus_heuristic=float(differences.mean()),
            descriptive_bootstrap_95_interval=np.quantile(means, [.025, .975]).tolist(),
            method="Resample seeds and shared zone indices; descriptive only, overlapping zones have spatial dependence; not a spatial confidence interval or superiority test")
        out["results"][str(radius)] = res
        print(f"radius {radius} km:", {k: round(v["fraction_all_pairs_connected"], 3) for k, v in res.items() if "fraction_all_pairs_connected" in v}, flush=True)
    (ROOT / "out" / "resilience_study.json").write_text(json.dumps(out, indent=2))
    print("wrote out/resilience_study.json")


if __name__ == "__main__":
    main()
