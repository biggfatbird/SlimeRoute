"""Render the final SLIMEROUTE video (v4.2 repaired), 1080x1350, ~28 s.

  growth of the Physarum network -> comparison with India's MAPPED rail lines (full-resolution GIS)
  -> block a region and watch it rewire -> honest scoreboard end card.

Needs out/fullres_rail_analysis.json (python research/fullres_rail_analysis.py) and
data/rail_lines_simplified.npz (written by the same script). FFmpeg must be on PATH.

    python research/render_final_video.py            # -> out/slime_india_final.mp4 + stills
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "research"))
import physarum_india as p  # noqa: E402
from fullres_rail_analysis import load_simplified  # noqa: E402

RAIL = "#5b9bd5"
GREEN = "#9be37a"


class RailScene(p.Scene):
    """The original scene, with mapped rail lines in place of the hand-picked schematic links."""

    def __init__(self, geo, rail_lines):
        super().__init__(geo)
        self.real_lc.remove()
        segs = [np.c_[p.proj(a[:, 0], a[:, 1])] for a in rail_lines]
        self.real_lc = LineCollection(segs, colors=RAIL, linewidths=0.55, zorder=2.2, capstyle="round")
        self.real_lc.set_visible(False)
        self.ax.add_collection(self.real_lc)
        self.legend.remove()
        handles = [Line2D([0], [0], color=p.ACCENT, lw=3.2), Line2D([0], [0], color=RAIL, lw=1.6)]
        self.legend = self.ax.legend(
            handles, ["Slime-mold network", "India's mapped railway lines"], loc="lower right",
            bbox_to_anchor=(0.985, 0.215), frameon=True, facecolor="#0b1118", edgecolor="#2a3b4e",
            labelcolor=p.TXT, fontsize=8.2, framealpha=0.92)
        self.legend.set_zorder(10)
        self.legend.set_visible(False)
        self.box.set_multialignment("left")
        for t in self.fig.texts:
            if t.get_text().startswith("Illustrative"):
                t.set_text("Rail lines: datta07/INDIAN-SHAPEFILES (third-party GIS). Outline and terrain costs are approximate.")

    def draw(self, *a, **k):
        super().draw(*a, **k)
        self.real_lc.set_alpha(min(0.8, k.get("overlay", 0.0) * 0.8))


def end_card(path, physarum, graph, rail, damage):
    """Scoreboard still. physarum/graph/rail: dict(detour, km); damage: dict(physarum, graph, mst) fractions."""
    fig = plt.figure(figsize=(p.W / p.DPI, p.HPX / p.DPI), dpi=p.DPI, facecolor=p.BG)
    T = lambda x, y, s, **kw: fig.text(x, y, s, **kw)  # noqa: E731
    T(0.07, 0.945, "ONE MORE TEST", color=p.ACCENT, fontsize=20, fontweight="bold", va="center")
    T(0.07, 0.855, "Is slime mold the best\nnetwork design?", color=p.TXT, fontsize=31, fontweight="bold",
      va="center", linespacing=1.15)
    T(0.07, 0.765, "MEAN ROUTE DETOUR BETWEEN THE 16 CITIES  (LOWER IS BETTER)", color=p.MUTED, fontsize=9.2, va="center")
    cols = [(0.20, physarum, "Physarum", p.ACCENT, f"{physarum['km']:,.0f} km network"),
            (0.50, graph, "Graph heuristic", GREEN, f"{graph['km']:,.0f} km network"),
            (0.80, rail, "Stitched GIS graph", RAIL, "entire network*")]
    for x, d, name, color, sub in cols:
        T(x, 0.675, f"{d['detour']:.2f}×", color=color, fontsize=38, fontweight="bold", ha="center", va="center")
        T(x, 0.612, name, color=p.TXT, fontsize=12, fontweight="bold", ha="center", va="center")
        T(x, 0.587, sub, color=p.MUTED, fontsize=9, ha="center", va="center")
    fig.add_artist(plt.Line2D([0.07, 0.93], [0.545, 0.545], color="#22313f", lw=1, transform=fig.transFigure))
    T(0.07, 0.485, "A simple graph heuristic found\nshorter routes at similar total length.", color=p.TXT,
      fontsize=17, fontweight="bold", va="center", linespacing=1.3)
    T(0.07, 0.355,
      f"Static, city-excluding zones (10-seed mean). Across {damage['sites']}\n"
      f"150 km blocked zones, Physarum kept all 120 city pairs\n"
      f"connected {damage['physarum']:.0%} of the time, vs {damage['graph']:.0%} for the graph heuristic\n"
      f"and {damage['mst']:.0%} for a plain spanning tree.\n"
      "Similar results are not a proven resilience advantage.",
      color="#cfd8e3", fontsize=12.2, va="center", linespacing=1.5)
    T(0.07, 0.235, "Takeaway: reinforcing busy routes grows connected, redundant\nnetworks. It does not magically beat engineers.",
      color=p.ACCENT, fontsize=12, va="center", linespacing=1.5)
    T(0.07, 0.105,
      "*GIS graph = the whole mapped network (about 86,000 km of line, parallel tracks included),\n"
      "Not an equal-cost comparison; junctions unverified. Seed-7 model, approximate terrain.\n"
      "Rail data: datta07/INDIAN-SHAPEFILES (third-party GIS). Model: Tero et al., Science 2010.",
      color="#6d7f91", fontsize=7.8, va="center", linespacing=1.55)
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba()).tobytes()
    fig.savefig(path, dpi=p.DPI, facecolor=p.BG)
    plt.close(fig)
    return buf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "out"))
    ap.add_argument("--seed", type=int, default=p.SEED)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    log = lambda m: print(f"[{time.time() - t0:6.1f}s] {m}", flush=True)  # noqa: E731

    fr = json.loads((out / "fullres_rail_analysis.json").read_text())
    aug = json.loads((out / "augmented_mst_metrics.json").read_text())
    bench = json.loads((out / "benchmark_metrics.json").read_text())
    rail_lines = load_simplified(ROOT / "data" / "rail_lines_simplified.npz")

    geo = p.build_geometry()
    slime = p.Slime(geo, args.seed)
    FR = dict(intro=36, grow=240, hold1=15, fade_in=36, compare=120, fade_out=20, block_in=24, repair=130,
              final=75, card=150)

    grow_idx = set(p.eased_steps(p.T_GROW, FR["grow"]).tolist())
    snaps_grow = [slime.D.copy().astype(np.float32)]
    for step in range(1, p.T_GROW + 1):
        slime.step()
        if step in grow_idx:
            snaps_grow.append(slime.D.astype(np.float32).copy())
    D_grown = slime.D.copy()
    before = p.analyse(geo, D_grown, slime.alive)
    log(f"grown: {before['total_km']:.0f} km, detour {before['detour']:.4f}")

    center = p.choose_block(slime, geo["city_xy"], p.BLOCK_R)
    slime.block(center, p.BLOCK_R)
    immediate = p.analyse(geo, slime.D, slime.alive)
    rep_idx = set(p.eased_steps(p.T_REPAIR, FR["repair"]).tolist())
    snaps_rep = [slime.D.astype(np.float32).copy()]
    alive_after = slime.alive.copy()
    for step in range(1, p.T_REPAIR + 1):
        slime.step()
        if step in rep_idx:
            snaps_rep.append(slime.D.astype(np.float32).copy())
    D_repaired = slime.D.copy()
    after = p.analyse(geo, D_repaired, slime.alive)
    (out / "recovery_v42.json").write_text(json.dumps(dict(seed=args.seed, before={k:v for k,v in before.items() if k != "mask"}, immediate={k:v for k,v in immediate.items() if k != "mask"}, after={k:v for k,v in after.items() if k != "mask"}, block_center=center.tolist(), radius_km=p.BLOCK_R), indent=2))
    log(f"after block: immediate {immediate['connected_pairs']}/120, adapted {after['connected_pairs']}/120")

    # sanity: the numbers on screen must equal the published JSON
    assert abs(before["detour"] - bench["unaffected"]["Physarum"]["mean_detour_reachable_only"]) < 1e-9, \
        "simulation no longer reproduces the published seed-7 numbers"

    prox = fr["proximity"]
    rd, pd, ad = fr["rail_topology"]["mean_detour"], before["detour"], aug["metrics"]["mean_detour_reachable_only"]
    pl, al = before["total_km"], aug["metrics"]["length_km_approx"]
    p10, a10 = prox["Physarum"]["model_length_within"]["10"], prox["Augmented MST"]["model_length_within"]["10"]
    compare_text = (
        "Mean route detour, 16 cities\n"
        f"  GIS graph, preliminary    {rd:4.2f}x\n"
        f"  Physarum        ({pl / 1000:4.1f}k km)  {pd:4.2f}x\n"
        f"  Graph heuristic ({al / 1000:4.1f}k km)  {ad:4.2f}x\n"
        "\n"
        "Network within 10 km of a rail line\n"
        f"  Physarum {p10:.0%}  |  Graph heuristic {a10:.0%}"
    )
    rewired_text = (
        f"Blocked zone radius       {p.BLOCK_R:.0f} km\n"
        f"Connected right after     {immediate['connected_pairs']}/{immediate['pairs']} pairs\n"
        f"Connected after adapting  {after['connected_pairs']}/{after['pairs']} pairs\n"
        f"Avg route detour          {before['detour']:.2f}x -> {after['detour']:.2f}x\n"
        "Global flow solve; each tube adapts from its own flux."
    )

    scene = RailScene(geo, rail_lines)
    vid = out / "slime_india_final.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{p.W}x{p.HPX}",
         "-r", str(p.FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(vid)], stdin=subprocess.PIPE)
    n = 0

    def emit(*a, **k):
        nonlocal n
        scene.draw(*a, **k)
        data = scene.grab()
        ff.stdin.write(data)
        n += 1
        return data

    def hold(data, k):
        nonlocal n
        for _ in range(k):
            ff.stdin.write(data)
            n += 1

    alive_all = np.ones(len(geo["I"]), dtype=bool)
    L1 = "Step 1  |  Start: all candidate connections are available"
    L2 = "Step 1  |  It keeps only the routes that carry flow"
    L3 = "Step 2  |  Compare with India's mapped railway lines"
    L4 = "Step 3  |  Block a major route and watch it rewire"
    DIM0 = 0.45
    data = emit(snaps_grow[0].astype(float), alive_all, L1, dim=DIM0)
    hold(data, FR["intro"])
    ng = max(len(snaps_grow) - 1, 1)
    for i, D in enumerate(snaps_grow[1:]):
        data = emit(D.astype(float), alive_all, L2, dim=DIM0 + (1 - DIM0) * min(1.0, i / (0.3 * ng)))
    hold(data, FR["hold1"])
    log("growth rendered")

    for i in range(FR["fade_in"]):
        a = (i + 1) / FR["fade_in"]
        data = emit(D_grown, alive_all, L3, overlay=a, box=dict(text=compare_text, alpha=a, legend=a > 0.5))
    scene.save_png(str(out / "slime_vs_real_rail.png"))
    hold(data, FR["compare"])
    for i in range(FR["fade_out"]):
        a = 1 - (i + 1) / FR["fade_out"]
        data = emit(D_grown, alive_all, L3, overlay=a, box=dict(text=compare_text, alpha=max(a, 0.01), legend=a > 0.5))
    log("comparison rendered")

    for i in range(FR["block_in"]):
        data = emit(D_grown, alive_all, L4, block=(i + 1) / FR["block_in"], block_center=center)
    for D in snaps_rep:
        data = emit(D.astype(float), alive_after, L4, block=1.0, block_center=center)
    data = emit(D_repaired, alive_after, L4, block=1.0, block_center=center, box=dict(text=rewired_text, alpha=1.0))
    scene.save_png(str(out / "slime_rewired_v42.png"))
    hold(data, FR["final"])
    log("disruption rendered")

    rj = json.loads((out / "resilience_study.json").read_text())
    res150 = rj["results"]["150"]
    damage = dict(sites=rj["sites_per_radius"],
                  physarum=res150["Physarum (10 seeds)"]["fraction_all_pairs_connected"],
                  graph=res150["Augmented MST"]["fraction_all_pairs_connected"],
                  mst=res150["Terminal MST"]["fraction_all_pairs_connected"])
    card = end_card(str(out / "scoreboard.png"),
                    dict(detour=pd, km=pl), dict(detour=ad, km=al), dict(detour=rd, km=fr["polyline_km"]), damage)
    hold(card, FR["card"])
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("FFmpeg failed")
    log(f"video written: {vid} ({n} frames, {n / p.FPS:.1f} s)")


if __name__ == "__main__":
    main()
