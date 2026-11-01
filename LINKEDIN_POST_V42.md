# LinkedIn caption - repaired local v4.2 supplement

Status: the public repository remains v4.1. This caption labels the additional work as a review supplement. The review-branch link below provides the supplement. Nothing has been posted automatically.

---

Can a slime-mold-inspired rule grow a useful transport network? I tested it on 16 Indian city points - then compared it with conventional graph algorithms.

The model solves flow through about 35,000 candidate grid connections. Routes carrying flow reinforce; unused routes fade. It is inspired by Tero et al.'s adaptive-network model, extended here with batched city-pair flows and approximate terrain costs.

What I found in this computational experiment:

- All ten seeds connected all 120 city pairs before damage. Mean model length was about 9,915 km, with 1.40x mean route detour.
- A conventional graph heuristic gave shorter routes at nearly equal length: seed-7 Physarum 1.34x versus heuristic 1.20x, at 10,035 versus 10,016 model-km.
- Across 300 shared 150-km-radius zones sampled from lattice locations away from cities, static networks retained all pairs in 96% of cases on average across ten Physarum seeds, versus 93% for the heuristic and 80% for the terminal MST baseline. Those first two are similar descriptive results, not a statistically proven win. There is no re-adaptation in this study.
- In one separate recovery demonstration, adaptation restored 105/120 pairs to 120/120, with detour increasing from 1.34x to 1.60x.

I also explored proximity to third-party mapped railway lines and a preliminary stitched GIS graph. That is a reference experiment, not a verified operational railway network or an equal-cost engineering comparison.

A useful lesson came from reproducibility: a fresh run agreed with the headline result, but stored edge masks were being interpreted differently on another environment. I added stable edge identities, checksums and regression tests, then regenerated the results.

Limits: approximate outline and synthetic terrain; no real demand, elevation or rivers; conditional static damage zones; unverified rail junctions and source currency. This is a research prototype, not railway planning software.

Public v4.1 code: https://github.com/biggfatbird/SlimeRoute
Additional analyses, tests and regenerated media (review branch, not merged): https://github.com/biggfatbird/SlimeRoute/tree/v4.2-review

Built with AI pair-programming assistance from Claude and ChatGPT. The repaired supplement was checked with automated tests and local reproduction runs.

Next: verified rail junctions, real demand and terrain, and stronger uncertainty analysis.

What would you test next?

#Python #NetworkScience #Biomimicry #ScientificComputing

---

Source comment: Tero et al., Rules for Biologically Inspired Adaptive Network Design, Science 327 (2010), https://doi.org/10.1126/science.1177894 . Railway GIS: datta07/INDIAN-SHAPEFILES; third-party mapped lines, not an official operational inventory.
