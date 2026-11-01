# SLIMEROUTE v4.1 — pre-publication technical audit

**Audit date:** 2026-11-01  
**Decision:** Publishable **as an explicitly scoped computational experiment** after pushing the verified repository and updating the caption URL. **Not research-grade infrastructure planning and not a validated replication of India’s operational railway graph.** No nontrivial simulation can truthfully be claimed limitation-free.

## Checks performed

1. Unpacked complete v4 release; inspected original model, benchmark scripts, GIS conversion, captions, provenance, and media.
2. Ran all **21 automated tests** successfully (including newly added tests of baseline metric consistency, handling null/malformed GeoJSON geometries, and implemented solver residual after a disruption).
3. Reran 450 Physarum growth iterations with seed 7: **saved network mask reproduced edge-for-edge**, 10,034.549882 model-km, detour 1.338409, all 120 city pairs connected.
4. **Fixed a real baseline objective bug:** v4 previously subtracted terrain-adjusted shortest-path distance from physical-path length when ranking augmentations. v4.1 uses terrain-adjusted cost for both terms, physical network length for the budget. Recomputed augmented mask, metrics, damage counts, GIS proximity and all comparison cards. The corrected baseline gives **10,016.249 model-km, detour 1.197691**, 120/120 pairs connected, and **18/25** connectivity-retaining fixed static damage sites.
5. Loaded source-derived rail-cell raster and recomputed all four 25-km/50-km proximity metrics. Physarum **89.20%**, corrected augmented graph **87.68%** at 25 km. These numbers measure *model length close to rail-cell centers*, **not railway reconstruction accuracy**.
6. Moved rail-cell centers by up to 0.1° in longitude/latitude (a simple sensitivity stress, not an uncertainty confidence interval): Physarum 25-km score moved between **87.23% and 90.66%**. Proximity is coarse, not precise.
7. Regenerated the 30.07-second H.264 **1080×1350** release video and its scientific endcards; made a post-production subtitle correction without modifying simulation frames. The full Matplotlib frame re-render exceeded execution limits in this session, so the video keeps the previously verified growth animation. Inspected the opening, algorithm-results and GIS-result frames.
8. Verified source-paper citation and existence of third-party GIS repository; added source, algorithm extension, licensing caution, cross-version history, and limitations to the README/research notes.

## What remains uncertain (disclose, do not hide)

| Category | Remaining risk | Why it matters |
|---|---|---|
| Railway data provenance | Full 34MB original line-geometry file was not re-downloaded or independently rasterized during this audit. Source Git blob identifier is documented, but the derived raster cannot by itself independently prove its own pedigree. | Do not claim full independent verification of original source-to-raster transformation. |
| Railway truth | Third-party track dataset may be dated, duplicated, mixed-gauge or inactive. A mapped line is not an official current operational graph. | Do not say "I recreated Indian Railways". |
| Spatial precision | 0.2° railway raster (~20km cell) and 25km tolerance. | A high nearby percentage does not mean matching track alignment/topology. |
| Network performance | No actual station-to-station rail graph, passenger demand, measured elevations, rivers, land/construction costs or schedule operations. | No realistic route-planning inference. |
| Geographic model | Handbuilt boundary, equirectangular network lengths, stylized regional terrain penalties; the data-derived boundary is optional and was not applied to these results. | Approximate model distances only. |
| Resilience study | 25 disruption locations are biased toward standard baseline routes; most scenarios test *static* connectivity, not adaptive repair. | No real flood probability or universal recovery conclusion. |
| Baseline fairness | Algorithms optimize different objectives; augmented heuristic nearly matches length budget but lacks a true Pareto frontier. | No generalized "biological design beats graph optimization" conclusion. |
| Software/platform | Tests executed locally in Python 3.13; CI for other runtimes is configured but not verified here; dependency ranges allow variation. | Verify GitHub Actions after push; include exact local versions if reproducing numerical environment. |

## Safe public claims

- "I built a numerical **Physarum-inspired** model connecting sixteen Indian city points on an approximate candidate grid."
- "I tested ten random seeds and 250 **static** damage cases; the original illustrative recovery run goes from 120/120, to 105/120, to 120/120 connected pairs after adaptation."
- "A corrected near-equal-length graph heuristic gave shorter model routes than the Physarum network for seed 7."
- "I examined **spatial proximity** to a **coarse raster derived from third-party mapped railway-line GIS**; it is not a rail-network topology comparison."

## Publication gate

- [x] Algorithm executes and original seed is reproducible
- [x] Baseline weighting inconsistency corrected
- [x] GeoJSON ingestion robustness regression tests
- [x] Updated figures, video and results agree
- [x] Algorithm paper and source GIS credited
- [ ] Independently inspect v4.1 GitHub release contents after uploading
- [ ] Replace `[ADD YOUR REAL REPOSITORY URL BEFORE POSTING]`
- [ ] Confirm video appearance/audio policy and caption on actual LinkedIn draft page
- [ ] Optional but necessary for a strong rail-engineering claim: audit the original line GIS snapshot, reconstruct true physical railway topology and compare routes at fixed terminals

**Bottom line:** The corrected artifact is credible as a small but substantive, transparent scientific-computing portfolio project; it is **not** flawless and should not be portrayed as such.
