"""Offline release gate for SLIMEROUTE v4.1.

Verifies JSON metrics against stored network masks and scene assets. It does NOT
prove that external GIS source-to-raster derivation is accurate, nor does it
reproduce all 10 seed dynamics. See AUDIT_REPORT.md.
"""
from pathlib import Path
import json,sys,math,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'research'))
from research.benchmark import network_metrics
import physarum_india as p


def check():
    out=ROOT/'out';g=p.build_geometry();mask=np.load(out/'baseline_masks.npz')
    bench=json.loads((out/'benchmark_metrics.json').read_text())
    augmented=json.loads((out/'augmented_mst_metrics.json').read_text())
    augmented_mask=np.load(out/'augmented_mst_mask.npy')
    assert augmented_mask.dtype==bool
    named={'Physarum':mask['Physarum'], 'terminal_MST_expanded':mask['terminal_MST_expanded'],
           'Delhi_shortest_path_union':mask['Delhi_shortest_path_union'],
           'augmented':augmented_mask}
    for name,m in named.items():
        source=augmented['metrics'] if name=='augmented' else bench['unaffected'][name]
        fresh=network_metrics(g,m)
        for key in ('length_km_approx','terrain_weighted_km_approx','mean_detour_reachable_only'):
            assert math.isclose(source[key],fresh[key],rel_tol=1e-9,abs_tol=1e-7),(name,key,source[key],fresh[key])
        assert fresh['connected_pairs']==120,(name,fresh)
    assert named['augmented'].sum()>0
    assert augmented['metrics']['length_km_approx']<=bench['unaffected']['Physarum']['length_km_approx']
    assert augmented['metrics']['mean_detour_reachable_only'] < bench['unaffected']['Physarum']['mean_detour_reachable_only']
    raster=np.load(ROOT/'data/rail_lines_raster_0p2deg.npy')
    from research.build_rail_raster import decode
    assert np.array_equal(raster,decode())
    rail=json.loads((out/'railway_geometry_comparison.json').read_text())
    assert rail['raster_grid']['occupied_cells']==3157
    # Current augmented-map proximity must be based on the *current* graph mask.
    from research.compare_rail_raster import rail_points,compare
    _,_,rr=rail_points()
    for name,key in [('Physarum','Physarum'),('Augmented_MST','augmented')]:
        m=named[key]
        fresh=compare(g,rr,m,thresholds=(25,50))
        for t in ('25','50'):
            got=rail['networks'][name]['thresholds'][t]['fraction_model_length_within_km_of_mapped_track_cells']
            expected=fresh['thresholds'][t]['fraction_model_length_within_km_of_mapped_track_cells']
            assert math.isclose(got,expected,abs_tol=1e-10),(name,t,got,expected)
    shifts=json.loads((out/'raster_position_sensitivity.json').read_text())
    assert len(shifts['perturbations'])==9
    video=out/'slime_india_v4.mp4'
    assert video.stat().st_size>200_000
    try:
        r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                          '-of','default=noprint_wrappers=1:nokey=1',str(video)],
                         check=True,capture_output=True,text=True)
        assert 29.5<float(r.stdout.strip())<30.5
    except FileNotFoundError:
        print('FFprobe unavailable; video duration not checked')
    print('PASS: saved graph masks, metrics, length budget, corrected heuristic, proximity, raster and media are internally consistent.')
    print('CAUTION: does not validate source GIS currency or physical railway topology.')

if __name__=='__main__':check()
