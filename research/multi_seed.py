"""Ten-seed study with common, independently chosen static damage locations."""
import json
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research.network_artifacts import load_masks
from research.benchmark import baselines,network_metrics,sample_damage_centers,blocked_mask,city_pair_mask
import physarum_india as p
SEEDS=[1,2,3,4,5,6,7,11,21,42]
RADIUS=150; SITES=25

def main():
    geo=p.build_geometry(); bases=baselines(geo)
    fixed_centers=sample_damage_centers(geo,np.logical_or.reduce(list(bases.values())),RADIUS,SITES,seed=20261031)
    expected=len(geo['names'])*(len(geo['names'])-1)//2;result=[]
    for seed in SEEDS:
        mask=load_masks(Path('out/physarum_seed_masks.npz'),geo)[str(seed)]
        baseline=network_metrics(geo,mask)
        counts=[network_metrics(geo,mask & blocked_mask(geo,c,RADIUS))['connected_pairs'] for c in fixed_centers]
        entry={'seed':seed,'no_damage':baseline,'damage_sites':SITES,
               'mean_remaining_pairs':float(np.mean(counts)),
               'min_remaining_pairs':int(np.min(counts)),
               'fraction_fully_connected':float(np.mean(np.array(counts)==expected)),
               'median_remaining_pairs':float(np.median(counts)),
               'all_remaining_pairs':counts}
        result.append(entry)
        out=Path('out/multi_seed_study.json');out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps({'seeds_predeclared':SEEDS,'iterations':p.T_GROW,
           'comparison':'same 25 fixed damage disks across seeds, sampled using baselines only, radius 150 km',
           'protocol':'Static network damage only. Adaptation after each failure NOT simulated.',
           'entries':result},indent=2))
        print(f'seed {seed:2d} length={baseline["length_km_approx"]:7.0f}km detour={baseline["mean_detour_reachable_only"]:.3f} intact_fraction={entry["fraction_fully_connected"]:.2f}',flush=True)
    print('FINISHED',flush=True)
if __name__=='__main__':main()
