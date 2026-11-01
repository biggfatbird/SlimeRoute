**Audited update 2026-11-01:** See `AUDIT_REPORT.md` for corrected augmented-MST scoring, regenerated metrics/videos, and additional test coverage. Historical figures below may mention the earlier heuristic.

# SLIMEROUTE v4 — Real mapped-rail geometry handoff (2026-10-31)

## Complete

- Preserved Claude's original Physarum flow-adaptation simulation and visual treatment.
- Preserved v3's ten-seed study, static damage scenarios, and four network-design comparisons.
- Inspected an independent 34MB railway-line GIS file from `datta07/INDIAN-SHAPEFILES` (Git blob `63ff14b3f3b62a6d18d4950e9ab4ba99a3c5c16d`). 29,946 LineStrings, 738,962 vertices, 29 state labels; a malformed/missing geometry excluded. Gauges include BG, MG, MTG and NG. This is georeferenced railway LINE geometry, not train-stop route pairs; complete operational validity is unverified.
- Created a 0.2° derived raster of the genuine mapped rail polylines with source-hash provenance and regeneration code. 3,157 occupied cells in a 133x150 grid.
- Calculated model-length-weighted proximity of every v3 network to the derived railway grid using WGS84-to-local AEQD coordinates and nearest-neighbor searches. Original simulation is not retrained and original model metrics remain unchanged.
- Generated `out/real_rail_geometry_comparison.png` and JSON evidence, added a 5-second geographic result card to the 25-second video: `out/slime_india_v4.mp4` (30.07s, 1080x1350, h264).
- 21 automated tests passing with Python.

## Core results

| Model | model length within 25km of mapped rail cell | within 50km |
|---|---:|---:|
| Physarum | 89.2% | 99.2% |
| Augmented MST | 87.7% | 98.1% |
| Terminal MST | 91.7% | 100% |
| Delhi-rooted shortest-path union | 79.8% | 98.2% |

**Do not call these railway-network reconstruction accuracy.** They are proximity to a coarse raster, with up to roughly 16km quantization error and no topology comparison. The 50km proximity saturates for all tested connected networks, so it is not distinguishing evidence. No full-resolution rail-line proximity analysis was executed here; only the source line geometry was independently inspected before rasterizing it. The third-party file's vintage and operational completeness are not verified.

## Reproduce

Offline from included raster and masks:
`python research/build_rail_raster.py && python research/compare_rail_raster.py && python -m pytest -q tests`

Full original source acquisition and independent validation on internet-connected machine:
`python research/download_real_tracks.py && python research/rasterize_external_tracks.py --tracks data/INDIAN_RAILWAYS.geojson --verify`

Optional higher-precision direct polyline proximity calculation once source is local:
`python research/compare_real_tracks.py --tracks data/INDIAN_RAILWAYS.geojson --out out/full_resolution_railway_comparison.json`

Reproduction note: If upstream source has changed, SHA validation fails deliberately. Check the new dataset and do not silently assume it reproduces this analysis.

## Files to publish

- `out/slime_india_v4.mp4`: 30-second social video
- `out/real_rail_geometry_comparison.png`: 16-city network and graph heuristic plotted over mapped rail grid
- `out/railway_geometry_comparison.json`: exactly reported coarse spatial metrics
- `LINKEDIN_POST.md`: fully qualified public caption
- `README.md` and `research/RESEARCH_NOTES.md`: complete methods, caveats and attribution
- `research/rasterize_external_tracks.py`, `research/download_real_tracks.py`: source reproduction

## Outstanding research work, not required for qualified LinkedIn disclosure

Construct a connected, verified **railway topology graph** using true track geometry and gauge/status attributes; locate 16 city station terminals, compare true rail shortest-path distances to simulated routes, use an up-to-date operations inventory, test demand-weighted resilience and improved terrain costs. This is not accomplished by a proximity heatmap. Avoid claiming otherwise.
