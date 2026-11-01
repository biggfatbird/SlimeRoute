# Current handoff — SLIMEROUTE v3

## Status: rigorous illustrative study; real-infrastructure evaluation incomplete

- Original 21-second model animation and code **preserved**. New 25.07-second social video adds an informative endcard; model calculations unchanged.
- Implemented and verified 3 different algorithmic grid-matched baselines (expanded terminal MST; Delhi-rooted shortest-path union; greedily augmented terminal MST near Physarum budget).
- Verified ten full 450-step seeds, 25 fixed spatial damage locations per seed, and seed-7 extraction-threshold and radius sweeps. Cross-seed damage evaluations are **static**, not post-damage adaptation.
- Verified numerical current conservation on grounded test graph; **14 automated tests pass**.
- Produced 4-way route figure, 10-seed robustness chart, blocked-radius sensitivity figure, source code, exact metrics and captions.
- Optional honest real-track GeoJSON parser with long segment rejection added, but has **NOT** been run on actual physical track GIS. Optional real boundary loader is also provided but not used for reported results.

## Read first

- README.md: run instructions and caveats.
- research/RESEARCH_NOTES.md: methodology and precise interpretation.
- research/REAL_DATA_GUIDE.md: links for physical railway GIS sources and mandatory checks.
- out/benchmark_metrics.json, out/augmented_mst_metrics.json, out/multi_seed_study.json and out/threshold_sensitivity.json: machine-readable evidence.
- LINKEDIN_POST.md: rigorous draft with no invented infrastructure claims. Add a real GitHub link.

## Critical remaining publication condition

**Do not describe the results as reconstruction or improvement of Indian Railways.** Obtain and validate physical track geometry and proper comparison methodology before making such a claim. Real elevation, rivers, construction constraints, passenger demand and formal matched-budget robustness evaluations are not yet included.
