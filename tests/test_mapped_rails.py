import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from build_rail_raster import decode
from compare_rail_raster import rail_points,compare
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import physarum_india as p

def test_decoded_raster_dimensions_and_occupancy():
    g=decode();assert g.shape==(133,150)
    assert g.dtype==bool
    assert g.sum()==3157

def test_geographic_coverage():
    g,coords,metric=rail_points()
    assert len(coords)==3157 and metric.shape==(3157,2)
    assert (coords[:,0]>68).any() and (coords[:,0]<95).any()
    assert (coords[:,1]>9).any() and (coords[:,1]<32).any()

def test_proximity_is_a_proportion():
    geo=p.build_geometry()
    import numpy as np
    from research.network_artifacts import load_masks
    masks=load_masks(Path(__file__).resolve().parents[1]/'out'/'baseline_masks.npz',geo)
    _,_,railmetric=rail_points()
    result=compare(geo,railmetric,masks['Physarum'],(25,50))
    for v in result['thresholds'].values():
        assert 0<=v['fraction_model_length_within_km_of_mapped_track_cells']<=1
        assert 0<=v['fraction_occupied_rail_cells_within_km_of_model']<=1
    a=result['thresholds']['25']['fraction_model_length_within_km_of_mapped_track_cells']
    b=result['thresholds']['50']['fraction_model_length_within_km_of_mapped_track_cells']
    assert a<=b

def test_rasterizer_small_geometry():
    from rasterize_external_tracks import rasterize_lines
    g,s=rasterize_lines([[[77.0,28.0],[77.25,28.0]],[[78.,18.],[78.2,18.2]]])
    assert s['accepted_lines']==2 and s['coordinate_vertices']==4
    assert g.sum()>=4
