"""Produce the review supplement's caption and machine-readable publication numbers."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'out'
read=lambda name:json.loads((out/name).read_text())
b=read('benchmark_metrics.json')['unaffected']['Physarum']
a=read('augmented_mst_metrics.json')['metrics']
f=read('fullres_rail_analysis.json')
r=read('resilience_study.json')['results']['150']
m=read('multi_seed_study.json')['entries']
rec=read('recovery_v42.json')
vals=dict(scope='Public v4.2 review branch; main remains v4.1',
    seed7=b,heuristic=a,ten_seed_mean_length_km=sum(x['no_damage']['length_km_approx'] for x in m)/len(m),
    ten_seed_mean_detour=sum(x['no_damage']['mean_detour_reachable_only'] for x in m)/len(m),
    ten_seed_all_connected=all(x['no_damage']['connected_pairs']==120 for x in m),
    preliminary_rail_detour=f['rail_topology']['mean_detour'],rail_polyline_km=f['polyline_km'],
    static_150km={k:r[k]['fraction_all_pairs_connected'] for k in ('Physarum (10 seeds)','Augmented MST','Terminal MST')},
    recovery=rec)
(out/'publication_numbers.json').write_text(json.dumps(vals,indent=2))
caption=f'''# LinkedIn caption - repaired local v4.2 supplement

Status: the public repository remains v4.1. This caption labels the additional work as a review supplement. The review-branch link below provides the supplement. Nothing has been posted automatically.

---

Can a slime-mold-inspired rule grow a useful transport network? I tested it on 16 Indian city points - then compared it with conventional graph algorithms.

The model solves flow through about 35,000 candidate grid connections. Routes carrying flow reinforce; unused routes fade. It is inspired by Tero et al.'s adaptive-network model, extended here with batched city-pair flows and approximate terrain costs.

What I found in this computational experiment:

- All ten seeds connected all 120 city pairs before damage. Mean model length was about {vals['ten_seed_mean_length_km']:,.0f} km, with {vals['ten_seed_mean_detour']:.2f}x mean route detour.
- A conventional graph heuristic gave shorter routes at nearly equal length: seed-7 Physarum {b['mean_detour_reachable_only']:.2f}x versus heuristic {a['mean_detour_reachable_only']:.2f}x, at {b['length_km_approx']:,.0f} versus {a['length_km_approx']:,.0f} model-km.
- Across 300 shared 150-km-radius zones sampled from lattice locations away from cities, static networks retained all pairs in {r['Physarum (10 seeds)']['fraction_all_pairs_connected']:.0%} of cases on average across ten Physarum seeds, versus {r['Augmented MST']['fraction_all_pairs_connected']:.0%} for the heuristic and {r['Terminal MST']['fraction_all_pairs_connected']:.0%} for the terminal MST baseline. Those first two are similar descriptive results, not a statistically proven win. There is no re-adaptation in this study.
- In one separate recovery demonstration, adaptation restored {rec['immediate']['connected_pairs']}/120 pairs to {rec['after']['connected_pairs']}/120, with detour increasing from {rec['before']['detour']:.2f}x to {rec['after']['detour']:.2f}x.

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
'''
(ROOT/'LINKEDIN_POST_V42.md').write_text(caption)
print('Wrote publication_numbers.json and the qualified local-supplement caption')
