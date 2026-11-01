"""Sensitivity to network extraction threshold and physical blockage radius.
This is postprocessing ONE seed-7 grown model, not a multi-gamma experiment.
"""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import physarum_india as p
from research.benchmark import network_metrics,city_pair_mask,blocked_mask,sample_damage_centers,baselines

if __name__=='__main__':
    g=p.build_geometry();s=p.Slime(g,7)
    for _ in range(p.T_GROW):s.step()
    centers=sample_damage_centers(g,np.logical_or.reduce(list(baselines(g).values())),150,25,seed=20261031)
    rows=[]
    for thr in [.05,.10,.15,.20,.25,.30]:
        mask=city_pair_mask(g,s.D,s.alive,thr)
        r=network_metrics(g,mask)
        rows.append({'threshold':thr,'model_metrics':r})
    radii=[]
    for rad in [75,100,150,200,250]:
        mask=city_pair_mask(g,s.D,s.alive,.15)
        counts=[network_metrics(g,mask & blocked_mask(g,c,rad))['connected_pairs'] for c in centers]
        radii.append({'radius_km':rad,'connected_pairs_mean':float(np.mean(counts)),
                      'fraction_fully_connected':float(np.mean(np.array(counts)==120)),
                      'minimum_pairs':int(min(counts))})
    doc={'seed':7,'iterations':p.T_GROW,'parameters_other_than_test':{'gamma':p.GAMMA,'I0':p.I0,'dt':p.DT},
         'network_extraction_threshold_study':rows,'damage_radius_study_same_25_fixed_centers':radii,
         'note':'Illustrative sensitivity analysis. Changing the mesh resolution, model parameters or real terrain could change all results.'}
    Path('out/threshold_sensitivity.json').write_text(json.dumps(doc,indent=2));print(json.dumps(doc,indent=2))
