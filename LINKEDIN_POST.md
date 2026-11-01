> HISTORICAL v4.1 / earlier document. For the repaired local supplement use README.md and REPAIR_REPORT.md. Its release status and numbers have not been updated here.

I gave a Physarum-inspired algorithm 16 Indian cities to connect. Then I tested its network against mapped Indian railway lines.

The animation looked convincing. The measurements told a more interesting story:

• About **89% of the simulated network's length** fell within 25 km of a mapped railway cell.
• In the other direction, only **18% of mapped railway cells** fell within 25 km of the simulated network.
• On the same simplified grid, a near-equal-length graph heuristic achieved shorter average routes: **1.20× vs 1.34×** detour.

I used a Physarum-inspired flow model, evaluated graph baselines, tested 10 random seeds, and examined 250 static damage scenarios.

This isn't a living slime mold, a recreated Indian Railways network, or infrastructure-planning software. The railway comparison uses coarse 0.2° cells from third-party mapped line geometry; the figures measure spatial proximity, **not track connectivity**.

Inspired by Tero et al. (*Science*, 2010). GIS: datta07/INDIAN-SHAPEFILES.

Code + reproducible experiments: [add the live URL of this repository when posting on LinkedIn]

What would you test next to distinguish a convincing map from a good network?

#Python #NetworkScience #ScientificComputing #Biomimicry
