# SLIMEROUTE v4.1 — Research and methodology notes (audited 2026-11-01)

This document describes **the audited release**, not the original tutorial-style demonstration. Historical notes are preserved in `RESEARCH_NOTES_V3_ARCHIVED.md`. For disclosure gates and provenance limitations, also read `../AUDIT_REPORT.md`.

## Research question

Can a **Physarum-inspired numerical rule**, applied to 16 geographically located Indian cities, form a connected transport-like network? How does its modeled route efficiency, infrastructure-length proxy, and survival of simulated interruptions compare with baseline graph algorithms? A separate, low-resolution map-proximity exercise asks whether the resulting networks lie **near cells containing third-party mapped railway-line geometry**. It does **not** test railway route topology or reconstruct Indian Railways.

## Physarum-like model

- Candidate graph: 6,092 nodes, 35,018 undirected edges; 25-km triangular lattice clipped to a manually approximated Indian outline. Geometric distance uses a single-latitude equirectangular projection, so network kilometers are **approximate model units** rather than surveyed distance.
- Geographic costs: `L_cost = L_physical * average(endpoint terrain multipliers)`; Himalayas, Thar, northeastern hills and Rann represented by smooth, manually specified cost fields. **Rivers, elevation rasters, traffic, construction permissions, cost of bridges and demand are excluded.**
- For each edge, flow is `Q_ij = D_ij (p_i - p_j) / L_cost,ij`. A sparse Kirchhoff system determines pressures. At each iteration, **12 randomized city origin–destination pairs** are independently solved, and `abs(Q)` is averaged over pairs. This multi-pair averaging is an **implementation extension**, not a literal reproduction of the precise procedure in Tero et al. (2010).
- Conductivity update: `D <- max(D + dt*(|Q|^gamma/(1+|Q|^gamma) - D), floor)` for live edges; chosen parameters: `dt=0.2`, `gamma=1.6`, `I0=5`, `450` growth iterations, fixed seed 7 for main figure.
- Route extraction: selected edges satisfy `D > 0.15 * max(live D)`; rendered faint tubes include weaker edges, so visual opacity must not be equated with metric inclusion.
- One 150-model-km disk blocks candidate edges; recovery means **newly reinforced pre-existing candidate mesh edges**, not construction of new physical infrastructure. In the showcased seed-7 case connectivity changes from `120/120` to `105/120` immediately after damage, back to `120/120` after 250 adaptation steps; detour worsens from `1.3384x` to `1.5993x`.

## Algorithmic controls, same candidate lattice, seed 7

| Approach | Approximate physical model length | Mean route detour (unweighted physical route / straight distance) | Connected city pairs |
|---|---:|---:|---:|
| Physarum-inspired | 10,034.55 km | 1.3384x | 120/120 |
| Expanded terminal MST (metric closure) | 6,335.99 km | 1.5762x | 120/120 |
| Delhi-rooted shortest-path union | 12,703.56 km | 2.0622x | 120/120 |
| **Augmented MST (corrected v4.1)** | **10,016.25 km** | **1.1977x** | 120/120 |

**Correction from v4**: An intermediate greedy MST augmentation compared physical-path distances against terrain-weighted distances when choosing candidate additions. v4.1 compares **terrain-weighted route costs to terrain-weighted route costs** and uses physical-length units only for the addition budget. The correction changes the selected mask, route metrics, and mapped-rail proximity. The stronger graph baseline **still** beats Physarum in this one setup, but this does not imply global superiority. This augmented method is a greedy heuristic, not an optimized Steiner network. Baseline objectives differ, and only the augmented baseline is close to the Physarum length budget. The design is not fitted to measured traffic.

## Robustness evaluation and uncertainty

- A predeclared ten-seed growth set `[1,2,3,4,5,6,7,11,21,42]` yields 120/120 connected terminal pairs for each seed. Mean modeled length `9,915.22`, sample SD `247.66`, mean detour `1.4033` and sample SD `0.0486`; **no universal performance guarantee**.
- Exactly 25 fixed 150-km disk centers are selected from areas carrying some edges of the *two original graph baselines*, with minimum separation and distance from cities. The same sites are applied to 10 Physarum seeds: **250 static damage checks**, 84% of which retain all city-pair connections. **These are not 250 simulated self-healing runs**. Center selection is conditioned on baseline links and is **not an unbiased geographic hazard distribution**; it could make baseline failures more frequent.
- On the same original 25 sites, the **corrected augmented MST** stays fully connected at **18/25**, with minimum `81/120` city pairs connected; the original seed-7 Physarum remains fully connected at 21/25. This is not a cost- and objective-matched resilience theorem.
- Radius sensitivity (seed 7, 25 fixed sites): retained full connectivity `96%` for 75-km disks, `20%` for 250-km disks. No adaptive recovery was performed during that radius sweep.
- The 15% threshold, stochastic pair draws, mesh scale, terrain multipliers, regularization, and flow parameters can materially affect other simulations. Numerical test: grounded Laplacian conservation residual `4.82e-13`; an additional test checks the implemented lightly-regularized solve after damage at a weaker tolerance.

## Third-party mapped railway line geometry — NOT topology

- Source: [datta07/INDIAN-SHAPEFILES](https://github.com/datta07/INDIAN-SHAPEFILES), `INDIA/INDIAN_RAILWAYS.geojson`, Git blob `63ff14b3f3b62a6d18d4950e9ab4ba99a3c5c16d`. Prior source inspection reported `29,946` mapped line features and `738,962` vertices. This is **third-party**, not a verified authoritative current operational inventory; data vintage and gauge/status coverage are uncertain.
- A derived occupancy raster is provided at `0.2°` geographic resolution (3,157 occupied cells), not full-resolution tracks. Model segments are geodesically sampled at ~5km interval and compared via nearest-neighbor proximity to occupied **cell centers** in a local azimuthal equidistant projection.
- 25-km proximity means **fraction of modeled network length** close to any occupied railway cell. It is **NOT fraction of railway track reconstructed**, correct routing, overlap of distinct track edges, or ability to build the network. Reverse fraction is by **count of occupied cells**, not railway km.

| Seed-7 network | Modeled length within 25km of a mapped rail cell | Within 50km |
|---|---:|---:|
| Physarum | 89.2% | 99.2% |
| Corrected augmented MST | **87.7%** | **98.1%** |
| Expanded terminal MST | 91.7% | 100.0% |
| Delhi shortest-path union | 79.8% | 98.2% |

The metric is weakly discriminating because rail line cells are geographically widespread. At a 25km threshold, a **half-cell coordinate perturbation** of the same raster-center points (not a true uncertainty confidence interval or a fresh source rasterization) changes Physarum's score to between `87.2%` and `90.7%`. Source: `out/raster_position_sensitivity.json`.

Full source GeoJSON (approximately 34MB) was **not included** in this project archive; the original-source SHA exists in the handoff and GitHub source. The independent full-source-to-raster equivalence check, and the optional full-resolution `compare_real_tracks.py` evaluation, **have not been completed in this audited environment**. An included decoder regenerates the raster encoding, but that is not independent provenance validation. Scripts permit verification against the source file on an internet-connected machine.

## Reproducibility and publication boundaries

- 21 tests pass in the audited Python environment. The base seed-7 `450`-iteration simulation was **rerun and matched the saved graph mask exactly**, yielding `10,034.549882` model km, `1.338409` detour, `120/120` pairs.
- Rebuild: `python scripts/prepublish_check.py` for consistency, `PYTHONPATH=. python -m pytest -q tests` for unit checks, or `bash scripts/rebuild_audited_media.sh` for fresh media after scientific changes (FFmpeg required).
- Cite Tero et al., *Science* (2010), DOI `10.1126/science.1177894`. Credit `datta07/INDIAN-SHAPEFILES` for the rail geometry derivative, which is distributed by its repository under MIT; downstream source licensing should be checked independently for any wider reuse.
- **Do not claim** this reconstructed, optimized or improved India's actual railway system, or that fault tolerance of an active physical slime mold or railway was experimentally measured.
