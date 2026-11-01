# SLIMEROUTE - repaired local v4.2 supplement

This regenerated supplement is published for review on the `v4.2-review` branch. The `main` branch remains v4.1; this has not been merged or declared a final release. The full rail GeoJSON is external on GitHub: download it with the hash-verifying script before running the strict gate. Start with `REPAIR_REPORT.md` for validation and limitations, and `LINKEDIN_POST_V42.md` for a caption that accurately labels this status.

## What it does

A Physarum-inspired numerical model connects 16 Indian city points on an approximate, terrain-weighted lattice. Kirchhoff flow is solved globally for random city-pair batches; tube conductivity adapts to flux. Conventional graph baselines share the candidate lattice. Static damage studies and a separate illustrative recovery demo measure different behaviors.

This is a computational prototype, not an operational railway model or planning software. The equations build on Tero et al., Science 327 (2010), DOI 10.1126/science.1177894. Parameters and extensions are described in `docs/history/README_v42_original.md`; that document's release instructions and historical numbers are not the current publication guide.

## Current outputs

- `out/slime_india_final.mp4`: regenerated silent portrait video.
- `out/slimeroute_carousel.pdf`: regenerated seven-slide carousel.
- `out/publication_numbers.json`: numbers used by the caption.
- `out/benchmark_metrics.json`, `out/augmented_mst_metrics.json`: same-grid comparison.
- `out/resilience_study.json`: 10 seeds, three radii, raw outcomes at 300 shared zones per radius.
- `out/fullres_rail_analysis.json`: proximity and preliminary stitched GIS graph, not verified rail junctions.
- `out/recovery_v42.json`: freshly reproduced single recovery demonstration.

Other old media and notes are retained as history. Use only the current outputs above for this supplement. The previous v4.1 video and audit are historical, not validation of this repaired build.

## Reproduce locally

Use Python 3.12 or another compatible supported Python with FFmpeg available on PATH. This build was checked locally on macOS with two numerical dependency sets; Linux CI is configured but not observed.

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# The full source is included in the local deliverable. If missing:
python research/download_real_tracks.py
bash scripts/reproduce_repaired.sh
```

For a validation-only run:

```sh
PYTHONPATH=. python -m pytest -q tests
python scripts/prepublish_check.py
python scripts/prepublish_check_v42.py
```

Both gates must pass. The strict gate fails if source geometry, mask identities or FFmpeg are absent. It verifies the actual rail-source hash, all stored seed/radius connectivity outcomes, a fresh seed-7 growth run, rail proximity/topology and current media. It does not re-grow every seed each time: `reproduce_repaired.sh` does that.

## Repair details

Candidate edges have canonical endpoint order. Every mask file has a `.identity.npz` sidecar containing explicit node coordinates, edge endpoints and a checksum of its paired mask. Loaders remap edge order and reject missing, altered or incompatible identities. Old unidentified masks must be regenerated; their edge meanings are not guessed.

The rail graph now deduplicates undirected links by minimum length, uses the model's lattice-snapped terminals and includes terminal access legs to rail vertices. These changes improve numerical consistency but do not verify real junctions. The approximately 86,000 km source total counts duplicate and parallel polyline geometry, not official railway route-km.

Resilience zones are sampled from lattice nodes farther than radius + 35 km from every city. Different radii use different eligible zones. Results are static connectivity tests, not disaster probabilities or general repair success. The descriptive paired bootstrap does not account for spatial dependence and is not a superiority test.

## Attribution

Code: project MIT license. Railway data and derivatives: `THIRD_PARTY_NOTICES.md`. Scientific source: Tero et al. (2010). AI-assisted original development and subsequent repair are disclosed in the caption.
