# LinkedIn post, v4.2 (paste the caption; attach out/slime_india_final.mp4 or out/slimeroute_carousel.pdf)

> Post only AFTER the v4.2 files are pushed to the GitHub repo (the caption cites analyses that live in them).
> Use the video OR the carousel as the main attachment. If you attach the PDF carousel, use the thumbnail
> `out/slime_vs_real_rail.png` as your first-comment image or skip it.

---

Can a slime-mold-inspired algorithm design a rail network for India? I tried to find out, and then tried to prove it wrong.

The question: given 16 Indian cities and ~35,000 candidate routes, what network emerges if every route simply thickens when it carries flow and fades when it doesn't? (Model: Tero et al., Science 2010, the Tokyo rail experiment.)

The method: sparse Kirchhoff flow on a terrain-weighted grid, then conductivity adaptation. 450 growth steps, 10 random seeds, graph-algorithm baselines on the same grid, and a damage test.

What came out:
→ All 10 seeds grew a fully connected network (~9,900 km, mean route detour 1.40×).
→ It did NOT beat a simple graph heuristic on route directness: 1.34× vs 1.20×, at nearly the same total length.
→ Where growth paid off was resilience: across 300 random 150 km blocked zones, Physarum kept all 120 city pairs connected 96% of the time (graph heuristic 93%, plain spanning tree 80%).
→ For scale: along India's mapped railway lines (third-party GIS), those same city pairs average a 1.26× detour, on a network with far more track (~86,000 km of line vs ~10,000 km).
→ In the recovery demo, a 150 km blockage cut 15 of 120 city pairs; after adaptation all 120 reconnected, with longer routes (1.34× → 1.60×).

Limits: approximate geography and synthetic terrain; no demand, elevation or rivers; damage tests are static; the rail GIS is third-party and my topology reconstruction is a first pass. This is a computational experiment, not a replica of Indian Railways and not planning software.

Next: real demand data, elevation and river costs, and a verified rail-graph comparison.

Code, tests and full method: github.com/biggfatbird/SlimeRoute

[Optional, recommended: "Built with AI pair-programming help (Claude, ChatGPT); I re-ran and checked every number."]

What would you test next?

#Python #NetworkScience #Biomimicry #ComplexSystems

---

## First comment (post right after publishing)

Sources: Tero et al., "Rules for Biologically Inspired Adaptive Network Design", Science 327 (2010), https://doi.org/10.1126/science.1177894 · Rail line GIS: datta07/INDIAN-SHAPEFILES (MIT) · Everything in the post is reproducible: `python research/fullres_rail_analysis.py`, `python research/resilience_study.py`, `PYTHONPATH=. python -m pytest -q tests`.

## Likely questions (short, honest answers)

- *Is this a real slime mold?* No. It is a mathematical model of Physarum's adaptation rule (Tero et al. 2010) run on a computer.
- *Does it recreate Indian Railways?* No. It connects 16 city points on an approximate grid. The rail comparison is a reference point, not a reconstruction.
- *Why is real rail's detour (1.26x) lower than Physarum's (1.34x)?* The real number is the whole mapped network, with about 8x the track of the model, so it is not a like-for-like cost comparison.
- *Why did the graph heuristic win on detour?* It optimizes route directness under a length budget directly; Physarum optimizes nothing explicitly and grows what the flow reinforces.
- *Is the damage test adaptive?* The 300-zone resilience study is static (no re-adaptation). The single recovery demo (105/120 to 120/120) is adaptive.
- *What did the 10 seeds show?* Growth variation only: lengths 9,515 to 10,405 km, mean detour 1.40x (SD 0.05).
