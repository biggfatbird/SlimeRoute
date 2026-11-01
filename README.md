# SLIMEROUTE — Physarum-inspired transport networks in India

An audited v4.1 **mathematical simulation** of adaptive slime-mold-like network growth across **16 Indian cities**, followed by a damage-and-recovery experiment. The numerical dynamics are inspired by **A. Tero et al., “Rules for Biologically Inspired Adaptive Network Design,” *Science* 327, 439–442 (2010), DOI: 10.1126/science.1177894**. This does not simulate an actual organism.

> **START HERE / CURRENT VIDEO:** [`out/slime_india_v4.mp4`](out/slime_india_v4.mp4) (30.07 seconds, silent). This is the **only video to upload to LinkedIn**. Older 21-second and 25-second demos are retained as historical assets, not evidence for v4.1.

> **Scope and evidence:** The **simulation** still uses an approximate Indian outline and synthetic terrain costs. Its original schematic-corridor benchmark is **not actual track geometry**. A separate **v4 spatial comparison** now uses a coarse raster derived from third-party mapped railway LineStrings, but this measures **proximity to occupied 0.2° cells**, not true track alignments, rail-network connectivity, operational services, route efficiency or validity for infrastructure planning. Neither result establishes that SLIMEROUTE reproduces Indian Railways.

## Run

Requires Python 3.10+, NumPy, SciPy, Matplotlib, and FFmpeg on `PATH`.

```bash
python -m pip install -r requirements.txt
python physarum_india.py --out out                # full 450 + 250 iteration simulation and ~21 s video
python physarum_india.py --quick --out out/quick  # fewer iterations / shorter draft; produces DIFFERENT metrics
python -m pip install pytest
PYTHONPATH=. python -m pytest -q tests
```

Legacy simulation outputs, retained for reproducibility and development history: `out/slime_india.mp4` (21-second historical demo), `out/slime_vs_schematic.png`, `out/slime_rewired.png`, and `out/metrics.json`. **These are not the final publication media.** The original Claude demo is archived as `out/claude_original_slime_india.mp4`. For posting, use only [`out/slime_india_v4.mp4`](out/slime_india_v4.mp4), with the current railway-proximity figures. The final video is silent.

## What is actually being modeled?

1. Project longitude/latitude into an **approximate equirectangular distance plane**. The approximation is not geodesically exact over the whole country.
2. Build a triangular lattice at **25 km** spacing, clipped to a **hand-drawn approximate country boundary**; each point connects to nearby points, making a 12-neighbor candidate mesh.
3. Assign each edge a terrain-adjusted cost proportional to length. The multipliers for the Himalayas, Thar, northeastern hills, and Rann are **hand-tuned smooth fields**, not measured topography, land costs, or actual constraints. **Rivers are not modeled**.
4. At each step, sample 12 random ordered city pairs. Set equal injected/withdrawn flow and solve Kirchhoff flow balance on the *whole* mesh using sparse LU.
5. For each candidate edge `i-j`, update conductivity using `D <- max(D + 0.2*(f(|Q|)-D), 1e-5)` with `f(Q) = Q^1.6/(1+Q^1.6)`; busy edges reinforce, idle edges decay. Computationally, the pressure solve has **global information**; the reinforcement rule acts on each edge.
6. After 450 iterations, consider an edge part of the displayed/analyzed network if `D > 0.15 * max(D)`. The 15% extraction threshold matters to reported connectivity and network length.
7. Choose a high-flow interior location for a 150 km radius blockage, **requiring that all city nodes remain connected on the original surviving candidate mesh**. This selection constraint makes the damage scenario less severe than an arbitrary failure.
8. Delete candidate edges touching the blocked disk and continue the *same* adaptation rule for 250 steps. Some low-conductivity pre-existing routes strengthen and reconnect the extracted network; this is rerouting within the candidate mesh, **not new physical track construction**.

The model parameters (seed 7, flow I₀=5, gamma=1.6, 12 city pairs per step, 450/250 iterations) were chosen for an illustrative connected outcome. They are not fitted or validated using measured physical slime mold experiments.

## Independently reproduced outputs — seed 7, full iteration counts

| Metric | Before damage | Immediately after block | After adaptation |
|---|---:|---:|---:|
| Extracted network length | 10,034.55 km | 9,451.54 km | 9,513.14 km |
| City pairs connected | **120/120** | **105/120** | **120/120** |
| Average detour | 1.3384× | 1.5237× on the 105 reachable pairs | 1.5993× |

The schematic city-link network has an illustrative 11,353.04 km total straight-segment length and a 1.1774× detour. **Do not interpret that as Indian Railways length or efficiency.** Using a 50 km distance threshold, 68.0% of the schematic segment samples fall near a strong simulated tube, and 87.3% of simulated tube **edges by count** fall near one of the schematic segments. Neither is proof of matching actual infrastructure.

The **immediate damage result is important**: for seed 7, the model temporarily loses connectivity for 15 city pairs when the thresholded network is inspected. After 250 adaptation steps, all 120 pairs reconnect, but paths become longer. The total length drops partly because edges were removed; it does **not** establish an improvement in engineering cost.

See `out/independent_reproduction.json` for exact rerun values, including the selected blockage center. For context, 120 is the number of distinct unordered city pairs, `16*15/2`.

## Extra seed sensitivity checks (same fixed parameters)

The complete growth (450 steps), disruption, and adaptation (250 steps) were also tested for seeds 11 and 21. These are **three illustrative runs**, not an exhaustive parameter study; the block location is selected anew for each seed.

| Seed | Before: connected pairs | Immediately after block | After adaptation | Avg detour, before → after |
|---|---:|---:|---:|---:|
| 7 | 120/120 | 105/120 | 120/120 | 1.338× → 1.599× |
| 11 | 120/120 | **120/120** | 120/120 | 1.363× → 1.645× |
| 21 | 120/120 | 81/120 | 120/120 | 1.464× → 1.623× |

In seed 11 the blocked location **did not disconnect the extracted network** at all; this is rerouting under disruption, not proof of recovery from network disconnection. Seeds 7 and 21 do show a temporary loss and subsequent restoration of city-pair connectivity. These results can be regenerated with `PYTHONPATH=. python scripts/seed_sensitivity.py 7 11 21`. Exact supplemental results: `out/sensitivity.json` (for seeds 11, 21) and `out/independent_reproduction.json` (seed 7).

**Visualization-versus-metric note:** faint tubes are drawn down to 3% of maximum conductivity for aesthetics, while graph metrics count only tubes above 15%. Therefore a faint visible filament may not be counted as part of the measured network.

## Baselines and limitations — updated in v4.1

- The original schematic-corridor image is **not a representation of actual Indian Railways**. For GIS-based analysis, use the separate coarse railway-cell comparison explained below.
- The four same-grid network designs were benchmarked; the near-length-matched augmented graph heuristic achieves a **shorter mean route detour** than the Physarum network for seed 7 (1.198× versus 1.338×). Their objectives and failure-handling differ, so this is **not proof of general superiority**.
- Ten growth seeds and 250 fixed-location **static** damage scenarios were tested; the separately described three-seed rerouting example is not a 250-scenario adaptive recovery experiment.
- Geographic cost fields, projection, grid spacing, network extraction threshold, and damage selection remain modeling assumptions; no population demand or real travel-time data were incorporated.
- The supplied rail-cell raster comes from a third-party mapped line-data source and does not establish present-day railway operations or network topology; independently rerasterizing the full source was beyond the v4.1 audit.
- The original DataMeet train-stop dataset is **not** used to infer physical track alignments.

## Data provenance / next milestone

- Modeling precedent: [Tero et al. (2010), *Science*](https://doi.org/10.1126/science.1177894)
- Potential real-world observational input: [DataMeet / railways (CC0)](https://github.com/datameet/railways). The repository provides station coordinates and train-route coordinate sequences, **not a guaranteed track-alignment dataset**. Not yet used for the reference lines in this version.
- Recommended next evaluation: obtain and validate true railway track GIS geometries (or explicitly label the DataMeet substitute as train-stop adjacency), independently compute an MST/grid-shortest-path baseline, then run multi-seed/parameter and fault-location experiments.

## Credits

Original prototype and visual composition were generated in a Claude Cloud session and subsequently reviewed, reproduced, tested, and relabeled with ChatGPT assistance. Adaptation equations derive from the cited scientific work. The original assets are retained under `out/claude_original_*` for provenance. Code is licensed under MIT (see `LICENSE`); the reference paper is **not** relicensed or reproduced here.

---

## Research upgrade (v3): stronger comparative study

The **original 21-second animation and model are preserved**. New components are *additional* evaluation tools, not a replacement of the previously reviewed demonstration.

### Run the new analyses

```bash
# Three same-grid graph baselines + 25 static spatial disruptions
python research/benchmark.py --seed 7 --damage-sites 25 --out out

# Greedy near-equal-budget MST reinforcement baseline
python research/equal_budget.py --budget-km 10034.549882328189 --out out

# LinkedIn-quality figures from verified metrics
python research/plot_benchmarks.py
python research/plot_fourway.py

# Independent ten-seed study (computationally intensive; 450 updates per seed)
python research/multi_seed.py

# Strict physical railway-track proximity evaluation, ONLY if actual railway polylines available
python research/compare_real_tracks.py --tracks data/rail_tracks.geojson --out out/real_rail_metrics.json

# Optional alternate boundary; new simulation outputs must be evaluated separately
python research/real_boundary.py --geojson data/india_adm0.geojson --seed 7

PYTHONPATH=. python -m pytest -q tests
```

**Research results, controls and limitations:** [`research/RESEARCH_NOTES.md`](research/RESEARCH_NOTES.md). **How to validate and refine railway geometry:** [`research/REAL_DATA_GUIDE.md`](research/REAL_DATA_GUIDE.md).

### Important controlled comparisons (seed 7)

| Same-grid algorithm | Modeled length | Mean all-pairs detour |
|---|---:|---:|
| Original Physarum | 10,035 km | 1.34× |
| Expanded terminal MST | 6,336 km | 1.58× |
| Delhi shortest-path union | 12,704 km | 2.06× |
| Greedy augmented MST (near Physarum length budget) | **10,016 km** | **1.20×** |

The augmented MST performs better than the Physarum model on those two metrics **for seed 7**. This is an informative negative control, not an embarrassment. Refrain from claiming biological design is superior to graph algorithms. All quantities above are from the original *approximate* geometry and terrain, not measured Indian track lengths. Source code, masks, and exact results are in `research/` and `out/`.

### Planned or unsupported upgrades — not silently claimed as complete

- Actual physical track alignment and current data vintages (not embedded; readers must acquire and verify)
- Accurate national projection and geodesic construction length on each candidate segment; use real elevation and river crossings
- Cost-matched Pareto-front comparisons and realistically modeled population/freight demand
- Repeated adaptive recovery for multiple predeclared spatial failures (the 25-site baseline comparison is **static**)
- Formal uncertainty across geographic assumptions and numerical model parameters

### Repeated-seed and disruption sensitivity (completed)

Ten full 450-step seeds: all ten connected 120/120 city pairs before damage, modeled length 9,515–10,405 km (mean 9,915 km), detour 1.338–1.464× (mean 1.403×). Across the 25 fixed spatial blockage locations applied to each network, **84% of 250 static scenarios** kept 120/120 pairs connected (per-seed 72–92%). **This is not 250 rerouting/recovery tests.** Details and raw per-scenario counts: `out/multi_seed_study.json` and `out/ten_seed_study.png`.

Seed-7 blocked radius sensitivity on those fixed sites: 75km 96% retain connectivity, 100km 92%, 150km 92%, 200km 60%, 250km 20%. The extracted seed-7 graph was unchanged for thresholds 0.05–0.30 of maximum conductivity; other parameters could change this. Output: `out/threshold_sensitivity.json`.

Video v3 with a graph-baseline result endcard: `out/slime_india_v3.mp4` (25.07 seconds; original reviewed 21-second video is still `out/slime_india.mp4`). Figures: `out/fourway_comparison.png`, `out/ten_seed_study.png`, `out/damage_radius_sensitivity.png`.

The **full-resolution physical railway geometry calculation has not been executed**; a separate v4 low-resolution, track-geometry-derived raster comparison is documented below. `research/compare_real_tracks.py` implements a strict optional ingestion/length-weighted spatial proximity evaluation, and `research/real_boundary.py` supports optional polygon-based geometry for *new* simulation runs. Neither module implies the original published metrics used those sources. See `research/REAL_DATA_GUIDE.md`.

---

## v4 — Actual mapped railway line geometry (coarse raster comparison)

This upgrade **uses railway-track line GIS from a third-party mapped-data repository**, rather than imaginary straight-line trunk corridors or DataMeet train stopping sequences.

**Source:** [datta07/INDIAN-SHAPEFILES](https://github.com/datta07/INDIAN-SHAPEFILES), `INDIA/INDIAN_RAILWAYS.geojson`, Git blob `63ff14b3f3b62a6d18d4950e9ab4ba99a3c5c16d` (29,946 line features; 738,962 coordinate vertices). The dataset includes broad, metre, mixed, and narrow-gauge labels; it has not been independently certified as complete, current, or all-operational. Attribution to the original GIS repository is required; do not claim it is official Indian Railways data.

**What was actually executed:** The mapped rail polylines were rasterized to **0.2° geographic cells** (~20 km spacing). The 16-city network and all three graph baselines were measured for geometric proximity to occupied railway cells (not rail-track topology). Model edges were sampled at ~5km spacing and model-length-weighted; the reverse railway result counts raster cells, not kilometers. See full details and numerical uncertainty in [`research/RESEARCH_NOTES.md`](research/RESEARCH_NOTES.md).

| Seed-7 design | Model length within 25 km of a mapped railway cell | Within 50 km |
|---|---:|---:|
| Physarum | 89.2% | 99.2% |
| Augmented MST | 87.7% | 98.1% |
| Terminal MST | 91.7% | 100% |
| Delhi shortest-path union | 79.8% | 98.2% |

**These percentages are NOT measured similarity with Indian Railways, nor evidence of superior railway design.** In the reverse direction, just **18.4% of occupied rail cells** have a model edge within 25 km for seed 7 (cell-count measure, not a proportion of railway length). The two denominators are different; quoting only 89.2% would give an incomplete impression. An approximately 20km cell resolution makes 25km proximity particularly uncertain; at 50km almost every connected candidate graph lies near a mapped railway. This suggests the metric is weakly discriminative. It is nevertheless a genuine comparison against line geometry rather than invented links.

**Run it with the supplied low-resolution, source-derived raster (offline):**

```bash
python research/build_rail_raster.py
python research/compare_rail_raster.py
python -m pytest -q tests
```

Produces `out/real_rail_geometry_comparison.png` and `out/railway_geometry_comparison.json`. The compact raster and its documented source SHA are bundled; the original 34MB railway source is not republished.

**Optional higher-precision analysis on a machine with web access:**

```bash
python research/download_real_tracks.py
python research/compare_real_tracks.py --tracks data/INDIAN_RAILWAYS.geojson --out out/full_resolution_railway_comparison.json
```

The downloader verifies the specific Git blob SHA before saving. **The optional full-resolution calculation was not run in this environment.** For a serious infrastructure comparison beyond map proximity, reconstruct a verified, topologically connected track graph and evaluate observed operational routes and true distance between the same terminals; this remains unfinished.

The original animated version and v3 benchmark outputs have been preserved unmodified. The final v4 animation adds a clearly labeled mapped-rail GIS result card; it does not alter growth or flow calculations.

To independently regenerate the raster **from the full original geometry**, run:

```bash
python research/download_real_tracks.py
python research/rasterize_external_tracks.py --tracks data/INDIAN_RAILWAYS.geojson --verify
```

This verifies the data snapshot's Git blob hash and confirms the 0.2° occupancy raster reproduces the published mask. The snapshot can change upstream; if the SHA check fails, inspect the new source rather than silently accepting different geometry.


## Audited release commands

```bash
PYTHONPATH=. python -m pytest -q tests
python scripts/prepublish_check.py
# To recreate simulation, network baselines, proximity figures and social media outputs
# from the existing source-derived raster (FFmpeg needed, rendering can take several minutes):
bash scripts/rebuild_audited_media.sh
```

For the precise package-audit environment (Python 3.13.5), see `requirements-audited.txt`. It is an environment snapshot, not a portable cross-platform lockfile. The included social video has an additional post-production subtitle correction; its numerically verified network is unchanged.

## Pre-publication audit (2026-11-01)

See [`AUDIT_REPORT.md`](AUDIT_REPORT.md) for confirmed tests, corrected unit-consistency issue in the augmented baseline, v4 raster uncertainty, the limited validity of the source GIS snapshot, and remaining research limitations. The archived files `HANDOFF.md` and `HANDOFF_V3.md` describe older versions; this README and `AUDIT_REPORT.md` are current.
