> Publication update: this repaired supplement is now on the `v4.2-review` branch for review. `main` remains v4.1. The report below records the preceding local repair. Rail source data must be downloaded separately on GitHub.

# SlimeRoute: repaired local v4.2 supplement

Prepared 1 November 2026. Public baseline: commit b2569515676ced94bcfe110a05b18ae17de1e1f6 in biggfatbird/SlimeRoute. The public repository was not modified, committed to or pushed to during this repair.

## Outcome

The previously failing stored-mask comparisons have been repaired locally. The original model equations remain unchanged. Candidate-edge ordering is now deterministic; masks include explicit geometry identities and a checksum. Existing unidentified masks were regenerated from the simulation and graph algorithms, not converted by guessing their edge meanings.

## Results regenerated

- Seed 7: 10,034.55 model-km; detour 1.338409; 120/120 connected pairs.
- Near-equal-length graph heuristic: 10,016.25 model-km; detour 1.197691; 120/120 connected pairs.
- Ten complete 450-step growth runs regenerated. Their masks and per-seed metrics are included.
- Shared 300-zone static damage results reproduced at radii 100, 150 and 200 km. At 150 km: Physarum 96.0% mean across ten seeds; heuristic 93.33%; terminal MST 79.67%; Delhi shortest-path union 60.67%.
- Single adaptive recovery rerun: 120/120 before, 105/120 immediately after damage, 120/120 after 250 repair steps; detour 1.338409 to 1.599279.
- Full-resolution rail proximity regenerated: Physarum 86.7484% and heuristic 86.0323% within 25 km of sampled railway geometry.
- Stitched rail-graph detour is now approximately 1.27x, rather than the original 1.26x. The repair removes repeated undirected graph links, uses the model's lattice-snapped terminals and includes terminal-to-vertex access legs. It does not validate actual junctions or operations. Consult out/fullres_rail_analysis.json for exact values and tolerance sensitivity.

## Why the original gates failed here

The original code reconstructed graph edges using the traversal order returned by a spatial tree. Historical masks stored only a boolean per edge, without recording edge endpoints. A fresh seed-7 run reproduced the headline metrics exactly, but its 315 selected edges disagreed with the stored 315-edge mask at 536 positions. Loading that historical mask against the local edge sequence produced a different network.

The repair sorts edges by endpoint identity and provides a sidecar for every mask file. The loader validates node coordinates and content checksum, remaps a changed edge order, and rejects a changed edge set or missing identity. Regression tests reproduce reordered-edge, missing-identity and modified-mask failures.

The original unidentified masks remain in the untouched baseline audit copy. The repair never claims to recover their undocumented original ordering.

## Scientific interpretation

These results show a computational trade-off, not a universal winner. The graph heuristic gives shorter routes at similar length. The resilience difference is descriptive: a paired seed/zone bootstrap spans zero, and it does not account for spatial dependence between overlapping zones. No statistically established resilience advantage is claimed. At 100 km the heuristic slightly exceeds the Physarum mean.

Zones are uniform over eligible lattice nodes, excluding centers within radius+35 km of cities. They are not real disaster samples; some zones can miss a network. Results describe static connectivity, not adaptive recovery or realistic flood risk. Different radii use different eligible sets.

The rail GeoJSON was independently downloaded and matches Git blob 63ff14b3f3b62a6d18d4950e9ab4ba99a3c5c16d. Its approximately 86,387 km is summed mapped polyline geometry including duplicates/parallel tracks, not official route-km. Endpoint proximity stitching does not identify verified junctions, stations, gauges, operating status or service routes. Distance projections still differ between model metrics and the rail reference. Proximity uses up-to-3-km sampling, not exact segment distance.

## Validation scope

36 tests pass with each numerical dependency set. The inherited graph/raster gate passes with each set. The strict v4.2 numerical checks pass with the recorded versions; the final complete source-and-media gate uses the current environment. See the logs for the exact completed checks.

Validation logs are included under validation/. Automated tests and the numerical consistency checks were run with both the recorded numerical package versions and the current versions selected by the allowed dependency ranges, on Python 3.12/macOS. The ten-seed generation used the recorded numerical versions. The video and carousel use freshly regenerated results. The strict publication gate validates actual source hash, explicit mask identities, all saved per-zone counts at all three radii, fresh seed-7 growth, regenerated heuristic, adaptive recovery, full-resolution rail analysis and current media. Missing source or FFmpeg is a failure, not a skipped PASS.

The gate checks all ten saved masks but re-grows only seed 7 during validation. The full reproduction script re-grows all ten seeds. Running the checks locally is not evidence that GitHub Actions or another operating system has passed. Cross-platform CI remains configured but unobserved. No external deployment or LinkedIn draft was created.

## Publication use

Use the regenerated video OR carousel, with LINKEDIN_POST_V42.md. That caption labels the extra analyses as a local supplement and identifies the public repository as v4.1. Do not claim that this repaired code is already public at that link. Share the supplement separately if promising reproducibility.

No additional permission or public-repository change is needed to review this local package. Publishing a repository update is a separate action.

Do not claim operational railway replication, infrastructure-planning readiness, universal recovery, proven resilience superiority, or paper/patent readiness. Verified rail topology, real demand and terrain, stronger spatial uncertainty analysis and a research novelty assessment remain future work.
