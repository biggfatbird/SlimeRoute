# CURRENT VERSION NOTE (2026-11-01)
This file retains historical v3 narrative. **Corrections** to the augmented MST method and the v4 rail-raster evaluation are documented in the main `README.md` and `AUDIT_REPORT.md`. New metrics supersede the older augmented MST values below.

# SLIMEROUTE — Evaluation report (v3)

## Research question and boundaries

Does a Physarum-style flow-adaptation rule produce a connected, compact network among 16 Indian city coordinates on a stylized terrain-adjusted lattice, and how does it trade off route detour, total infrastructure length, and sensitivity to spatial disruptions against simple **same-grid** routing baselines?

This is **not** a comparison with Indian Railways. Neither railway-line geometry nor empirical passenger/freight demand nor real elevation are used in the reported results.

## Method

The original simulation's triangular lattice, 25 km approximate spacing, 16 city nodes, 12 stochastic source–sink pairs per update, and conductance update are retained. Growth lasts 450 updates for seed 7. Conductivity threshold 0.15× maximum defines extracted network edges. Terrain penalties are synthetic fields for the Himalayas, Thar, northeastern hills, and Rann. Kirchoff flows are solved using sparse LU, with a small diagonal regularization in the original simulation. An independent grounded-Laplacian current conservation test is included.

### Baselines

- **Metric-closure terminal MST expanded onto candidate grid**: build weighted grid shortest paths between terminals, compute minimum spanning tree over the complete 16-terminal metric closure, expand selected paths to lattice edges. This is an approximation for connecting terminals, **not** exact Steiner tree or a length-optimal unconstrained engineering solution.
- **Delhi shortest-path union**: union shortest terrain-weighted grid paths from Delhi to all 15 other cities. A rooted design does **not** optimize all-pairs path length and is intentionally a simple second baseline.

Both use exactly the original candidate mesh and terrain-weighted lengths to choose paths. We report geometric edge length, terrain-weighted construction proxy, and observed route detour over connected pairs separately. **Network lengths differ**, so we do not claim fair performance at matched cost.

### Damage protocol

For an initial **static** benchmark, sample 25 spatially separated centers from the union of the initial three evaluated networks, exclude centers within 185 km of any city, and remove candidate edges touching a 150 km radius disk. Every network is evaluated against exactly these same centers; no scenario is rejected for disconnecting cities. Unlike the original animated seed-7 repair demonstration, these baseline damage results do **not** allow additional adaptation/reconstruction after the cut.

The sample is conditional on being near *at least one route*, not representative of flood risk across all India. It measures graph disconnection, not physical recoverability.

## Core reproducible results — seed 7

See `out/benchmark_metrics.json` for full precision and `out/damage_locations.csv` for the actual spatial scenarios. The result for the expanded MST is inexact by design, as above.

| Design | Approx. total physical length | Terrain-weighted length proxy | Average path detour | Pairs connected |
|---|---:|---:|---:|---:|
| Physarum-inspired | 10,035 km | 10,461 km | 1.338× | 120/120 |
| Expanded terminal MST | 6,336 km | 6,691 km | 1.576× | 120/120 |
| Delhi shortest-path union | 12,704 km | 13,082 km | 2.062× | 120/120 |

The Physarum solution is shorter than the Delhi-rooted baseline, but longer than the terminal MST, with shorter all-pairs detours than either. **This is a trade-off, not optimization dominance**. All distances use the legacy approximate projection, not true geodesic route distance.

## Threats to validity and next upgrades

1. **Infrastructure**: Real railway tracks have not been incorporated; scripts are provided for verified railway-line geometry, but results must not be implied without obtaining and validating it.
2. **Geography**: boundary, distance projection and terrain are simplified. River crossings and slope/elevation are absent. Real travel costs, route demand, protected land and population distributions are absent.
3. **Algorithm scope**: 16 predetermined terminals, not the national transport task. Stochastic source/sink sampling is a modeling decision, not observed traffic. Conductance threshold materially changes extracted paths.
4. **Comparisons**: baseline networks have different budgets; neither is an optimized non-tree redundancy baseline. Stronger studies require fair equal-cost augmentation and Pareto frontier comparisons.
5. **Robustness**: damage centers conditional on active routing, block radius chosen in advance, static loss differs from adaptation over 250 steps. Adaptation only uses remaining candidate edges; no new physical railway is constructed.
6. **Numerics**: sparse flow solver uses weak regularization, and the independent test uses a grounded graph. More solver tolerances, mesh resolutions and limits remain to be assessed.
7. **Reproducibility**: pinned seed, parameter documentation, 21 regression tests and output JSON; a fully pinned dependency lockfile and independent platform testing are still advisable.

**Correct public-facing description:** “I built a Physarum-inspired numerical experiment that connected 16 Indian cities and tested its routing/robustness trade-offs against two graph algorithms.” Do not call it a validated transportation design.

## Stronger near-equal-budget heuristic (additional result)

The extra file `research/equal_budget.py` begins with the terminal MST and greedily adds full terrain-weighted shortest paths between high-detour city pairs while staying under the seed-7 Physarum **physical-length budget** (10,034.55 model-km). This is a greedy strategy, not an optimal solution and not a perfect budget match. It achieves **10,016.25 km** and **1.1977×** average detour, compared with **10,034.55 km** and **1.3384×** for Physarum. It keeps 120/120 pairs connected. The more demanding baseline therefore beats Physarum on two efficiency metrics in this seed. The seed-7 damage centers used for the original three-network benchmark also yielded 21/25 intact outcomes for this heuristic; this is a specific static test, not full equivalence of adaptive recovery.

This result is **essential** for publication credibility. The argument is no longer “biological model outperforms algorithms,” but “bio-inspired rules self-organize a connected, redundant graph, with trade-offs revealed by stronger algorithmic controls.”

## Publicity guardrails

A 25-km grid and a handcrafted country outline are adequate for an illustrative mathematical study, not an engineering claim about the national rail map. A web-accessible railway data catalog has been located, and strict GeoJSON ingestion and checks are implemented, but **the full-resolution source geometry has not been independently rerun in this audited build; a coarse source-derived raster has been compared**. The project should not be described as a verified India Railways recreation.

## Ten-seed robustness study (completed)

A predeclared set of ten seeds, `[1,2,3,4,5,6,7,11,21,42]`, was run for the full 450 original growth steps per seed with the same parameters. All ten extracted networks connected all **120/120** city pairs before damage. Model length averaged **9,915.22 km**, with **247.66 km sample SD**, spanning **9,514.93–10,404.65 model-km**. Mean detour averaged **1.4033×**, with **0.0486 sample SD** and a range **1.3384–1.4643×**.

Twenty-five *fixed* damage centers were chosen from the **two standard graph baselines**, independently of the Physarum runs, with radius 150 model-km. Each of the ten networks was tested at these same 25 locations. Across the 250 static damage scenarios, **84%** retained all 120 city connections, with per-seed fully connected site rates of **72–92%**. No recovery dynamics were evaluated for these 250 scenarios; don't describe this as a 250-run self-healing study. The sampling still reflects baseline-network locations rather than a real probabilistic flood hazard map. See `out/multi_seed_study.json` and `out/ten_seed_study.png`.

## Postprocessing sensitivities (completed)

With seed 7 fixed, changing the extraction threshold between **0.05 and 0.30 of maximum conductance** made no difference to the selected network in this example. This suggests a strong separation in final conductivities for this particular seed, **not** proof the threshold never matters. Across the same 25 preselected damage sites, the fraction of sites keeping all 120 city connections fell from **96%** for 75-km blocking radius to **20%** for 250-km radius. No adaptive recovery was simulated in these radius sweeps. See `out/threshold_sensitivity.json` and `out/damage_radius_sensitivity.png`.

**Open methodological gaps:** sensitivity to gamma/current/mesh, real elevation and rivers, cost-calibrated baselines, genuine railway-line datasets, independent physical validation, geographic uncertainty, and construction feasibility. No one should describe the experiment as limitation-free.

## v4 — Mapped railway line geometry: coarse spatial validation (2026-10-31)

An additional, independent geospatial source has now been inspected: `datta07/INDIAN-SHAPEFILES/INDIA/INDIAN_RAILWAYS.geojson`, Git blob SHA `63ff14b3f3b62a6d18d4950e9ab4ba99a3c5c16d`. It contains 29,946 LineString features, 738,962 coordinate vertices, 29 state-name groups, and gauge values BG/MG/MTG/NG. A separate malformed/non-LineString feature is excluded. This is **mapped railway line geometry**, unlike the DataMeet train-stop paths. The source is third-party, its field `FTR_CRY` appears to represent gauge, and neither its construction year nor operational completeness has been independently validated. It should not be called a current operational inventory. All mapped lines, not only passenger-service rail, were included.

To fit the rail geometry into the reproducible bundle without republishing the whole 34MB source, railway vertices/segments were rasterized onto an approximately 0.2° WGS84 grid. The process samples each original railway segment at <=0.08° intervals, rounds locations to the nearest 0.2° cell, and stores a compact occupied-cell mask (3,157 cells). **This is a derived low-resolution raster; it is not a surveyed track geometry representation.** The model and baseline edges were sampled at approximately 5km intervals, converted to a centered azimuthal equidistant coordinate system, then compared to nearest occupied rail-cell centers with `scipy.spatial.cKDTree`. Model-near-rail fractions are weighted by model edge length; the reverse rail-cell-near-model fractions are **cell-unweighted** and must not be described as percentages of physical rail length. At this resolution, an occupied railway-cell point is typically displaced from the source track by up to about 16 km, so fine tolerances (especially 25 km) have nontrivial rasterization error. The reference source's approximate raw polyline length is 86,355 km, but counts parallel tracks and duplicates and **is not Indian Railways route-km**.

Seed-7 model-length-weighted proximity:

| Network | Fraction within 25km of mapped rail cells | Fraction within 50km |
|---|---:|---:|
| Physarum | 89.2% | 99.2% |
| Augmented MST | 87.7% | 98.1% |
| Terminal MST | 91.7% | 100.0% |
| Delhi-rooted shortest-path union | 79.8% | 98.2% |

**Interpretation: proximity saturates for all methods at 50km because railway coverage is geographically widespread. This is not meaningful proof of network similarity or an empirical win.** Any publication must show that graph baselines do just as well or better on this weak map-proximity metric. The sources do not allow claims that the Physarum network reconstructed actual routing links, their distances, operating lines or real traffic.

Machine-readable results: `out/railway_geometry_comparison.json`. Source-derived low-resolution rail mask: `data/rail_lines_raster_0p2deg.npy`; regeneration: `python research/build_rail_raster.py`. Plot: `out/real_rail_geometry_comparison.png`. To independently obtain the original track GIS and run the full-line evaluator at higher precision on an internet-connected machine: `python research/download_real_tracks.py`, then `python research/compare_real_tracks.py --tracks data/INDIAN_RAILWAYS.geojson --out out/full_resolution_railway_comparison.json`. The full-resolution calculation **was not executed here**; do not imply otherwise. SHA verification intentionally fails if source changes, requiring a new audit. Ensure source license attribution (INDIAN-SHAPEFILES MIT repository) when publishing derivatives.
