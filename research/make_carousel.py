"""LinkedIn carousel (PDF + PNG pages, 1080x1350 each) built from the repository's own result files.

    python research/make_carousel.py        # -> out/slimeroute_carousel.pdf and out/carousel/slide_*.png
Run research/render_final_video.py first (it writes slime_vs_real_rail.png and scoreboard.png).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
BG, TXT, MUTED, GOLD, GREEN, BLUE = "#070a0f", "#eef2f6", "#8ea0b2", "#ffb02e", "#9be37a", "#5b9bd5"
TEAL, PURPLE, PANEL, LINE = "#6dd3cc", "#b08cf0", "#0f1720", "#22313f"
W, H, DPI = 1080, 1350, 150
N_SLIDES = 7


def page(n):
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=BG)
    fig.text(0.07, 0.027, "SLIMEROUTE", color=MUTED, fontsize=8, fontweight="bold", va="center")
    fig.text(0.93, 0.027, f"{n} / {N_SLIDES}", color=MUTED, fontsize=8, ha="right", va="center")
    return fig


def full_image(fig, path):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(plt.imread(path))
    ax.axis("off")
    ax.set_zorder(0)


def style_axes(ax):
    ax.set_facecolor(PANEL)
    for s in ax.spines.values():
        s.set_color(LINE)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    ax.grid(color=LINE, lw=0.6, alpha=0.7)
    ax.set_axisbelow(True)


def slide_cover(n):
    fig = page(n)
    fig.text(0.07, 0.963, "SLIMEROUTE", color=GOLD, fontsize=12, fontweight="bold", va="center")
    fig.text(0.07, 0.862, "I asked a slime-mold\nalgorithm to connect\n16 Indian cities.", color=TXT, fontsize=25.5,
             fontweight="bold", va="center", linespacing=1.15)
    fig.text(0.07, 0.738, "Then I tested it against India's real railway map,\nand against simple graph algorithms.",
             color=MUTED, fontsize=12.5, va="center", linespacing=1.45)
    img = plt.imread(OUT / "slime_vs_real_rail.png")
    ax = fig.add_axes([0.04, 0.085, 0.92, 0.6])
    ax.imshow(img[200:1235, 60:1020])
    ax.axis("off")
    fig.text(0.93, 0.055, "Swipe  →", color=GOLD, fontsize=13, fontweight="bold", ha="right", va="center")
    return fig


def slide_rule(n, gamma):
    fig = page(n)
    fig.text(0.07, 0.93, "FLOW-DRIVEN ADAPTATION", color=GOLD, fontsize=13, fontweight="bold", va="center")
    fig.text(0.07, 0.865, "How the network grows", color=TXT, fontsize=30, fontweight="bold", va="center")
    rows = [("1", "Push flow", "Random city pairs send current through the whole mesh\nof ~35,000 candidate routes (a global flow solve)."),
            ("2", "Reinforce", "Each route thickens or thins based on its own flux."),
            ("3", "Fade", "Unused routes decay. What survives is the network.")]
    y = 0.74
    for num, head, body in rows:
        fig.text(0.07, y, num, color=BG, fontsize=15, fontweight="bold", ha="center", va="center",
                 bbox=dict(boxstyle="circle,pad=0.45", fc=GOLD, ec=GOLD))
        fig.text(0.15, y + 0.012, head, color=TXT, fontsize=19, fontweight="bold", va="center")
        fig.text(0.15, y - 0.042, body, color="#cfd8e3", fontsize=12.2, va="center", linespacing=1.5)
        y -= 0.165
    fig.add_artist(plt.Rectangle((0.07, 0.115), 0.86, 0.12, transform=fig.transFigure, fc=PANEL, ec=LINE, lw=1))
    fig.text(0.5, 0.195, r"$D \leftarrow D + \Delta t\,\left(f(|Q|) - D\right),\quad f(Q)=\frac{Q^{\gamma}}{1+Q^{\gamma}}$",
             color=TXT, fontsize=15, ha="center", va="center")
    fig.text(0.5, 0.145, f"D = tube thickness, Q = flow, γ = {gamma}.  Model: Tero et al., Science 2010 (Tokyo rail).",
             color=MUTED, fontsize=9, ha="center", va="center")
    return fig


def slide_image(n, name):
    fig = page(n)
    full_image(fig, OUT / name)
    return fig


def slide_tradeoff(n, multi, bench, aug, res):
    fig = page(n)
    fig.text(0.07, 0.945, "TRADE-OFFS, NOT A WINNER", color=GOLD, fontsize=13, fontweight="bold", va="center")
    fig.text(0.07, 0.895, "Shorter routes or more resilience?", color=TXT, fontsize=24, fontweight="bold", va="center")

    ax = fig.add_axes([0.11, 0.50, 0.83, 0.31])
    style_axes(ax)
    L = np.array([e["no_damage"]["length_km_approx"] for e in multi]) / 1000
    D = np.array([e["no_damage"]["mean_detour_reachable_only"] for e in multi])
    ax.scatter(L, D, s=34, color=GOLD, alpha=0.55, zorder=3, label="Physarum, 10 seeds")
    ax.scatter([L.mean()], [D.mean()], s=150, color=GOLD, edgecolor="white", lw=1.2, zorder=4)
    pts = {"Terminal MST": (bench["unaffected"]["terminal_MST_expanded"]["length_km_approx"] / 1000,
                            bench["unaffected"]["terminal_MST_expanded"]["mean_detour_reachable_only"], TEAL),
           "Delhi star": (bench["unaffected"]["Delhi_shortest_path_union"]["length_km_approx"] / 1000,
                          bench["unaffected"]["Delhi_shortest_path_union"]["mean_detour_reachable_only"], PURPLE),
           "Graph heuristic": (aug["metrics"]["length_km_approx"] / 1000, aug["metrics"]["mean_detour_reachable_only"], GREEN)}
    offsets = {"Terminal MST": (10, 8), "Delhi star": (-62, -20), "Graph heuristic": (12, -4)}
    for name, (x, y, c) in pts.items():
        ax.scatter([x], [y], s=150, color=c, edgecolor="white", lw=1.2, zorder=4)
        ax.annotate(name, (x, y), xytext=offsets[name], textcoords="offset points", color=c, fontsize=10, fontweight="bold")
    ax.annotate("Physarum", (L.mean(), D.mean()), xytext=(14, 14), textcoords="offset points", color=GOLD, fontsize=10,
                fontweight="bold")
    ax.set_xlabel("Total network length (thousand km, approximate)", color=MUTED, fontsize=9)
    ax.set_ylabel("Mean route detour (lower is better)", color=MUTED, fontsize=9)
    ax.set_xlim(5.5, 14)
    ax.set_ylim(1.1, 2.2)
    fig.text(0.11, 0.835, "Lower-left is better on both axes.  Small gold dots = 10 random seeds.", color=MUTED, fontsize=9.5,
             va="center")

    r = res["results"]["150"]
    names = ["Delhi star", "Terminal MST", "Graph heuristic", "Physarum"]
    keys = ["Delhi shortest-path union", "Terminal MST", "Augmented MST", "Physarum (10 seeds)"]
    vals = np.array([r[k]["fraction_all_pairs_connected"] for k in keys]) * 100
    cols = [PURPLE, TEAL, GREEN, GOLD]
    ax2 = fig.add_axes([0.11, 0.115, 0.83, 0.27])
    style_axes(ax2)
    ax2.bar(names, vals, color=cols, width=0.62, zorder=3)
    sd = r["Physarum (10 seeds)"]["fraction_sd_across_seeds"] * 100
    ax2.errorbar([3], [vals[3]], yerr=[sd], color="white", capsize=4, lw=1.4, zorder=4)
    for i, v in enumerate(vals):
        ax2.text(i, v + sd + 2.5 if i == 3 else v + 1.5, f"{v:.0f}%", ha="center", color=TXT, fontsize=12, fontweight="bold")
    ax2.set_ylim(0, 118)
    ax2.set_ylabel("% of zones", color=MUTED, fontsize=9)
    ax2.tick_params(axis="x", labelsize=9.5, colors=TXT)
    fig.text(0.07, 0.425, "All 120 pairs connected after 150-km static damage",
             color=TXT, fontsize=11, fontweight="bold", va="center")
    fig.text(0.07, 0.062, "Static, city-excluding lattice zones; no re-adaptation. Physarum bar: mean of 10 seeds, error bar = 1 SD.\n"
             "Approximate geography and synthetic terrain.", color=MUTED, fontsize=7.8, va="center", linespacing=1.5)
    return fig


def slide_limits(n):
    fig = page(n)
    fig.text(0.07, 0.94, "HONEST SCORECARD", color=GOLD, fontsize=13, fontweight="bold", va="center")
    fig.text(0.07, 0.885, "What this experiment shows", color=TXT, fontsize=25, fontweight="bold", va="center")
    blocks = [("SHOWS", GREEN, ["Flux-driven reinforcement grows a connected, redundant\n16-city network (10 of 10 seeds)",
                              "Under random damage it is about as resilient as a\npurpose-built graph heuristic, and more resilient than these tree baselines"]),
              ("DOES NOT SHOW", "#ff7a7a", ["That slime mold beats engineers: a simple graph\nheuristic found shorter routes",
                                            "That it reproduces Indian Railways: no verified junctions,\ntopology or demand",
                                            "Real elevation, rivers or construction cost"]),
              ("NEXT", BLUE, ["Real population and freight demand",
                              "Rivers and elevation in the cost model",
                              "Validate physical junctions and station-level routes"])]
    y = 0.80
    for head, color, items in blocks:
        fig.text(0.07, y, head, color=color, fontsize=12.5, fontweight="bold", va="center")
        y -= 0.04
        for it in items:
            lines = it.count("\n") + 1
            fig.text(0.09, y - 0.012 * (lines - 1), "•  " + it.replace("\n", "\n    "), color="#dbe3ec", fontsize=11.6,
                     va="center", linespacing=1.45)
            y -= 0.046 + 0.026 * (lines - 1)
        y -= 0.022
    fig.add_artist(plt.Line2D([0.07, 0.93], [0.135, 0.135], color=LINE, lw=1, transform=fig.transFigure))
    fig.text(0.07, 0.093, "Public v4.1 code; extra results in the local v4.2 supplement.", color=TXT, fontsize=11.5, fontweight="bold", va="center")
    fig.text(0.07, 0.058, "Model: Tero et al., Science 327 (2010).  Rail GIS: datta07/INDIAN-SHAPEFILES (third-party).",
             color=MUTED, fontsize=8.6, va="center")
    return fig


def main():
    multi = json.loads((OUT / "multi_seed_study.json").read_text())["entries"]
    bench = json.loads((OUT / "benchmark_metrics.json").read_text())
    aug = json.loads((OUT / "augmented_mst_metrics.json").read_text())
    res = json.loads((OUT / "resilience_study.json").read_text())
    for need in ("slime_vs_real_rail.png", "scoreboard.png", "fourway_comparison.png"):
        if not (OUT / need).exists():
            sys.exit(f"missing out/{need}; run research/render_final_video.py first")
    slides = [slide_cover(1), slide_rule(2, 1.6), slide_image(3, "slime_vs_real_rail.png"), slide_image(4, "scoreboard.png"),
              slide_tradeoff(5, multi, bench, aug, res), slide_image(6, "fourway_comparison.png"), slide_limits(7)]
    # full-bleed image slides already carry their own footers; drop the generic page chrome there
    for i in (2, 3, 5):
        for t in list(slides[i].texts):
            t.remove()
    for index, fig in enumerate(slides):
        if index in (2, 3, 5):
            continue
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        for text in fig.texts:
            bounds = text.get_window_extent(renderer)
            if bounds.x0 < -1 or bounds.x1 > fig.bbox.width + 1:
                raise ValueError(f"Slide {index+1} text exceeds page width: {text.get_text()}")
    (OUT / "carousel").mkdir(exist_ok=True)
    with PdfPages(OUT / "slimeroute_carousel.pdf") as pdf:
        for i, fig in enumerate(slides, 1):
            fig.savefig(OUT / "carousel" / f"slide_{i}.png", dpi=DPI, facecolor=BG)
            pdf.savefig(fig, facecolor=BG)
            plt.close(fig)
    print("wrote out/slimeroute_carousel.pdf and out/carousel/slide_1..7.png")


if __name__ == "__main__":
    main()
