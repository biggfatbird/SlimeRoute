# SLIMEROUTE v4.2 — additions to the audited v4.1 release (2026-11-01)

v4.2 is **additive**. No audited v4.1 file, number or figure was changed (README gets one pointer block; `INTEGRITY.sha256` and the CI workflow gain the new files/step). It closes the two open items in `AUDIT_REPORT.md`: *"full 34 MB source not re-downloaded"* and *"reconstruct physical railway topology and compare routes at fixed terminals"* (first-pass version).

## What is new

| File | Purpose |
|---|---|
| `research/fullres_rail_analysis.py` | Full-resolution analysis of the 34 MB rail GeoJSON: proximity at 5/10/25/50 km, and a stitched rail graph for real route distances between the 16 cities |
| `research/resilience_study.py` | 300 uniformly random blocked zones per radius (100/150/200 km), identical for every design, Physarum over 10 seeds |
| `research/render_final_video.py` | 27 s video: growth, **real rail lines** (replaces the hand-picked schematic links), damage and rewiring, honest scoreboard |
| `research/make_carousel.py` | 7-slide LinkedIn carousel built from the result files |
| `scripts/prepublish_check_v42.py` | Offline gate; recomputes the new numbers (and, if the source file is present, the full-resolution ones) |
| `tests/test_fullres.py` | 7 tests on toy geometries with known answers |
| `out/fullres_rail_analysis.json`, `out/resilience_study.json` | Results |
| `out/slime_india_final.mp4`, `out/slimeroute_carousel.pdf`, `out/carousel/`, `out/scoreboard.png`, `out/slime_vs_real_rail.png` | Publish assets |
| `data/rail_lines_simplified.npz` | Rail lines simplified to ~1 km (355 KB) so media can be re-rendered without the 34 MB download. Derived from datta07/INDIAN-SHAPEFILES (MIT) |
| `LINKEDIN_POST_V42.md` | Caption, first comment, reply notes |

## Evidence for each new claim

| Claim (as worded in the caption) | Source of the number | Check |
|---|---|---|
| Physarum 1.34x, heuristic 1.20x, 10,035 vs 10,016 km | `out/benchmark_metrics.json`, corrected `out/augmented_mst_metrics.json` (v4.1) | `prepublish_check.py` |
| 10/10 seeds fully connected, ~9,900 km, detour 1.40x | `out/multi_seed_study.json` | recomputed from entries |
| Real mapped rail averages 1.26x between the 16 cities | `out/fullres_rail_analysis.json` (`rail_topology`) | stitching tolerance 0.1 / 0.3 / 0.6 / 1.5 km gives 1.267 / 1.265 / 1.263 / 1.254; recomputed from the SHA-verified source by `prepublish_check_v42.py` |
| Rail has ~86,000 km of line vs ~10,000 km | same JSON (`polyline_km`; parallel/duplicate tracks counted) | |
| 96% / 93% / 80% / 61% of random 150 km zones keep all 120 pairs connected (Physarum / heuristic / MST / Delhi star) | `out/resilience_study.json` | Physarum seed 7 and the three static designs recomputed by `prepublish_check_v42.py` |
| Recovery demo 105/120 to 120/120, detour 1.34x to 1.60x | `out/metrics.json` (v4.1) | `tests`, reproduced from scratch |

Source of the rail GIS: `datta07/INDIAN-SHAPEFILES/INDIA/INDIAN_RAILWAYS.geojson`, git blob `63ff14b3f3b62a6d18d4950e9ab4ba99a3c5c16d`. Re-downloaded and the blob SHA verified on 2026-11-01 (the audit had not done this).

## Corrections relative to the coarse raster (v4.1)

At full resolution the share of network length within 25 km of mapped rail is **86.7%** for Physarum and **86.0%** for the corrected heuristic (raster: 89.2% and 87.7%). The raster over-estimated both by about 2 points. At 10 km the terminal MST (63.6%) is closer to the mapped lines than Physarum (52.7%). Proximity at 50 km is ~97-100% for every design and carries no information. v4.1's "89%" statements stay in the v4.1 files as audited history; use the full-resolution numbers going forward.

## Resilience: why the 84% / 92% / 96% figures differ

Earlier damage tests used 25 sites drawn along the networks' own routes (and different site sets in different scripts), which is a harsh, route-targeted test: the corrected heuristic keeps all pairs in 18 of 25 (72%). v4.2 draws 300 centres uniformly at random (skipping centres within radius + 35 km of a city), so no design is favoured. Do not compare across radii: the exclusion rule shifts the eligible sites as the radius grows. With 300 zones the binomial standard error is about 1.1 points at 96%, so Physarum (96.0%, SD 2.6 across seeds) and the heuristic (93.3%) are close; both are clearly above the tree designs.

## Not validated / known limits

- The rail GIS is third-party; its completeness, vintage, gauge mix and operational status are unverified. The real-rail detour is for the *whole* mapped network (about 8.6x the track of the 16-city models), so it is a reference point, not a like-for-like comparison.
- The rail graph is stitched from line ends within 0.6 km and cities snap to the nearest rail vertex (max 3.6 km). It is not a station-level operational graph and ignores service patterns.
- Model detours use the project's equirectangular lattice; the rail detour uses an azimuthal-equidistant projection. The ratio difference is small (a couple of percent) but not zero.
- Resilience tests are static; only the single seed-7 demo re-adapts. Geography and terrain are approximate; no demand, elevation or rivers.
- Tests ran locally on Python 3.13 only; GitHub Actions has not been observed on this branch.

## Reproduce

```bash
pip install -r requirements.txt
python research/download_real_tracks.py          # 34 MB, SHA-verified -> data/INDIAN_RAILWAYS.geojson
python research/fullres_rail_analysis.py
python research/resilience_study.py              # ~5 min on 2 cores
python research/render_final_video.py            # ~2 min, needs ffmpeg
python research/make_carousel.py
PYTHONPATH=. python -m pytest -q tests && python scripts/prepublish_check.py && python scripts/prepublish_check_v42.py
```
