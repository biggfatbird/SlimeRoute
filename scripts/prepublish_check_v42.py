"""Strict local publication gate. Missing source, mask identity or FFmpeg is a failure."""
from pathlib import Path
import json
import math
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from research import fullres_rail_analysis as fr
from research.network_artifacts import load_masks, load_mask
from research.resilience_study import sample_sites, survival, summarize, SEEDS, RADII
from research.benchmark import baselines, city_pair_mask
from research.media_validation import check_media
import physarum_india as p


def check_resilience(out, geo):
    rs=json.loads((out/'resilience_study.json').read_text())
    masks=load_masks(out/'physarum_seed_masks.npz',geo)
    base=baselines(geo)
    designs={'Terminal MST':base['terminal_MST_expanded'], 'Delhi shortest-path union':base['Delhi_shortest_path_union'],
             'Augmented MST':load_mask(out/'augmented_mst_mask.npy',geo)}
    assert rs['physarum_seeds']==SEEDS
    for rad in RADII:
        centers=sample_sites(geo,rad,rs['sites_per_radius'],rs['site_seed'])
        result=rs['results'][str(rad)]
        for name, mask in designs.items():
            fresh=summarize(survival(geo,mask,centers,rad))
            assert fresh=={k:result[name][k] for k in fresh},(rad,name)
        fractions=[]
        for seed in SEEDS:
            fresh=summarize(survival(geo,masks[str(seed)],centers,rad))
            assert fresh==result['Physarum (10 seeds)']['per_seed'][str(seed)],(rad,seed)
            fractions.append(fresh['fraction_all_pairs_connected'])
        assert math.isclose(np.mean(fractions),result['Physarum (10 seeds)']['fraction_all_pairs_connected'],abs_tol=1e-12)
        assert math.isclose(np.std(fractions,ddof=1),result['Physarum (10 seeds)']['fraction_sd_across_seeds'],abs_tol=1e-12)
    model=p.Slime(geo,7)
    for _ in range(p.T_GROW):model.step()
    assert np.array_equal(city_pair_mask(geo,model.D,model.alive,p.REL_THR),masks['7']), 'Fresh seed 7 differs from cached mask'
    assert np.array_equal(masks['7'],load_masks(out/'baseline_masks.npz',geo)['Physarum'])
    from research.equal_budget import augmented_tree
    fresh_heuristic,_=augmented_tree(geo,json.loads((out/'augmented_mst_metrics.json').read_text())['budget_km'])
    assert np.array_equal(fresh_heuristic,designs['Augmented MST']), 'Heuristic mask does not reproduce'
    before=p.analyse(geo,model.D,model.alive)
    center=p.choose_block(model,geo['city_xy'],p.BLOCK_R)
    model.block(center,p.BLOCK_R)
    immediate=p.analyse(geo,model.D,model.alive)
    for _ in range(p.T_REPAIR): model.step()
    after=p.analyse(geo,model.D,model.alive)
    recovery=json.loads((out/'recovery_v42.json').read_text())
    for name,actual in [('before',before),('immediate',immediate),('after',after)]:
        for key,value in actual.items():
            if key!='mask': assert math.isclose(value,recovery[name][key],rel_tol=1e-9,abs_tol=1e-10),(name,key)
    print('PASS: reproduced heuristic and single adaptive recovery',flush=True)
    print('PASS: all 10 saved masks, all 3 radii, raw per-zone connectivity, and fresh seed 7',flush=True)


def check_rail(out,geo):
    j=json.loads((out/'fullres_rail_analysis.json').read_text())
    source=ROOT/'data/INDIAN_RAILWAYS.geojson'
    fr.verify_source(source)
    lines,total=fr.load_lines(source)
    V,start,lens=fr.lines_to_km(lines)
    fr.assert_physical_tracks(V,start,lens)
    lon,lat=p.unproj(geo['pts'][geo['city_node'],0],geo['pts'][geo['city_node'],1])
    x,y=fr.TO_M.transform(lon,lat); terminals=np.c_[x,y]/1000
    topo=fr.rail_topology(V,start,lens,terminals)
    for k,v in topo.items():assert math.isclose(v,j['rail_topology'][k],rel_tol=1e-9,abs_tol=1e-10),(k,v,j['rail_topology'][k])
    assert topo['pairs_connected']==120
    assert total==j['features_total'] and len(lines)==j['features_used']
    for t in (.1,.3,1.5):
        value=fr.rail_topology(V,start,lens,terminals,t)['mean_detour']
        assert math.isclose(value,j['rail_detour_vs_stitch_tolerance_km'][str(t)],rel_tol=1e-9)
    a,b=fr.segment_indices(start,lens); rp,rw=fr.sample_segments(V,a,b)
    assert math.isclose(rw.sum(),j['polyline_km'],rel_tol=1e-12)
    for name,mask in fr.network_masks(out,geo).items():
        fresh=fr.proximity(rp,rw,geo,mask)
        for field in ('model_length_within','rail_length_within_model'):
            for t in fr.TOLERANCES_KM:
                assert math.isclose(fresh[field][str(t)],j['proximity'][name][field][str(t)],abs_tol=1e-10),(name,field,t)
    assert len(fr.load_simplified(ROOT/'data/rail_lines_simplified.npz'))==len(lines)
    print('PASS: actual source hash, full-resolution proximity, topology and stitch sensitivity',flush=True)


def main():
    geo=p.build_geometry();out=ROOT/'out'
    check_resilience(out,geo);check_rail(out,geo);check_media(out)
    print('PASS: strict v4.2 local gate; GIS operational truth and cross-platform CI remain unvalidated')
if __name__=='__main__':main()
