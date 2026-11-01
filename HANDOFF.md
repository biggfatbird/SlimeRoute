> **Historical handoff (original prototype).** For current results and publication use `README.md`, `AUDIT_REPORT.md`, and `PUBLISH_CHECKLIST.md`. The instructions and caption mentioned below describe the earlier schematic-only build.

# SLIMEROUTE handoff — 31 October 2026

## What was received

Two identical `physarum_india.py` copies, two identical READMEs, two identical draft LinkedIn posts, one 21.07-second 1080×1350 H.264 MP4, and one comparison PNG. No downloaded DataMeet raw datasets or actual boundary GeoJSON were included. This project is a **continuation of the provided source**, not a ground-up replacement.

## Audit completed

- Inspected all of the simulation code and media.
- Reproduced the full 450+250-step seed-7 trajectory independently; `out/independent_reproduction.json` has exact results.
- Verified 6 automated tests (geometry/projection/city connectivity/determinism/blocking/schematic baseline).
- Corrected **real-trunk** comparison claims to **schematic links**, because no actual railway GIS data are used.
- Added immediate-after-block connectivity reporting: seed 7 goes 120/120 → 105/120 → 120/120 (the last recovery requires 250 further steps).
- Re-rendered the 21-second video and comparison/damage figures using the corrected source.
- Added full-length seed 11 and seed 21 sensitivity runs, with results in `out/sensitivity.json`.
- Rewrote the README and LinkedIn caption with accurate qualifiers; added `requirements.txt`, tests, `.gitignore`, and license.

## Important scope gaps

1. **Actual Indian Railways track alignment is NOT compared.** The DataMeet repo has rail station coordinates and train stop sequences; those aren't actual surveyed tracks. A true real-data comparison needs independent geospatial alignment data and QA.
2. Terrain multipliers and India outline are hand-drawn approximations, not official boundary/elevation/river vectors. No big rivers have been modeled.
3. Only three seeds and one gamma/current/threshold/radius setting evaluated. No MST, shortest-path, or measured infrastructure baseline yet.
4. The disruption site is chosen to preserve connectivity on the full underlying mesh, making the experiment conditional. Faint visible tubes are not necessarily counted in the measured network.

## How to continue

1. Obtain/download the boundary and track-alignment GIS datasets to `data/` and record versions, URLs, licenses and dates. Do not confuse train stop-to-stop straight segments with physical track geometry.
2. Build a geodesic distance/CRS-consistent comparison, not a fixed-equirectangular map for national-scale measurement.
3. Add 10+ seeds across multiple damage locations, vary gamma and threshold; compare cost/detour/connectivity with MST and shortest-path baselines.
4. Produce v3 of the social demo from independently validated outputs and publish with a clear methods/limitations link.

## Running and posting

See README for commands. `LINKEDIN_POST.md` is an accurate caption *for the simulation as it exists today*, with an explicit schematic reference caveat. Replace its repository URL placeholder after uploading code. Do not post using Claude's original caption claim that all pairs stayed connected through disruption; only the restored network has 120/120 for seed 7.
