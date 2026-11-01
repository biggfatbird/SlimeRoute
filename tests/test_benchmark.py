"""Independent test coverage for baseline and geospatial logic."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
from research.benchmark import baselines,network_metrics,candidate_graph,flow_residual,blocked_mask,city_pair_mask,sample_damage_centers
from research.compare_real_tracks import read_lines, sample_lines,segments_from_lonlat,compare
import physarum_india as p

@pytest.fixture(scope='module')
def geo():return p.build_geometry()

@pytest.fixture(scope='module')
def base(geo):return baselines(geo)

def test_both_baselines_connect_16_cities(geo,base):
    for k,mask in base.items():
        r=network_metrics(geo,mask)
        assert r['connected_pairs']==120,k
        assert r['length_km_approx']>1000
        assert r['terrain_weighted_km_approx']>=r['length_km_approx']

def test_flow_conservation_grounded_laplacian(geo):
    sl=p.Slime(geo,7)
    for _ in range(3):sl.step()
    result=flow_residual(geo,sl)
    assert result['max_nodal_flux_error']<1e-6

def test_threshold_extraction_is_explicit(geo):
    sl=p.Slime(geo,7);D=np.ones(len(geo['I']));D[0]=10
    assert city_pair_mask(geo,D,sl.alive,.5).sum()==1

def test_damage_sites_no_city_overlap_and_spatial_separation(geo,base):
    candidates=np.logical_or.reduce(list(base.values()))
    centers=sample_damage_centers(geo,candidates,150,10)
    for center in centers:
        assert np.min(np.linalg.norm(geo['city_xy']-center,axis=1))>185
    assert len(centers)==10

def test_track_loader_and_proximity_synthetic(tmp_path,geo):
    # A short real-geometry-like polyline fixture, not claimed to be railway data.
    f=tmp_path/'two_tracks.geojson';f.write_text('''{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"LineString","coordinates":[[77,23],[77.02,23.04],[77.1,23.12]]}}]}''')
    pts,weights,km,n,skipped=sample_lines(read_lines(f),spacing_km=2)
    assert n==1 and skipped==0 and 0<km<30
    assert len(pts)==len(weights) and np.isclose(weights.sum(),km)

def test_train_stop_leaps_are_rejected(tmp_path):
    f=tmp_path/'leaps.jsonl'
    f.write_text('{"type":"Feature","geometry":{"type":"LineString","coordinates":[[72,19],[88,22]]}}\n')
    with pytest.raises(ValueError,match='train-stop route'):
        sample_lines(read_lines(f))

def test_real_boundary_accepts_polygon_rejects_line(tmp_path):
    from research.real_boundary import load_mainland
    a=tmp_path/'polygon.geojson';a.write_text('{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[68,8],[98,8],[98,37],[68,37],[68,8]]]}}')
    ring=load_mainland(a)
    assert len(ring)==5 and np.isclose(ring[:,0].min(),68)
    a.write_text('{"type":"Feature","geometry":{"type":"LineString","coordinates":[[68,8],[98,8],[98,37]]}}')
    with pytest.raises(ValueError,match='Polygon/MultiPolygon'):
        load_mainland(a)

def test_augmented_baseline_is_within_budget_and_connected(geo):
    from research.equal_budget import augmented_tree
    # A tighter synthetic budget avoids heuristic comparisons to generated files.
    m, additions=augmented_tree(geo,10034.549882328189)
    result=network_metrics(geo,m)
    assert result['length_km_approx']<=10034.549882328189 + 1e-6
    assert result['connected_pairs']==120
    assert len(additions)>0


def test_augmented_selection_uses_same_weighting_for_both_route_costs(geo,monkeypatch):
    # Regression: routing gap must not subtract a terrain-cost shortest route
    # from a physical-length current route (inconsistent objective).
    import research.equal_budget as eb
    original=eb.candidate_graph
    seen=[]
    def spy(g,active=None,weighted=True):
        seen.append(weighted)
        return original(g,active,weighted=weighted)
    monkeypatch.setattr(eb,'candidate_graph',spy)
    m,_=eb.augmented_tree(geo,10034.549882328189)
    assert seen and all(seen),f'inconsistent route-cost weighting: {set(seen)}'
    assert network_metrics(geo,m)['connected_pairs']==120

def test_physarum_actual_solver_residual_after_damage(geo):
    # Evaluate the implemented weakly-regularized solve, not only the independent
    # grounded Laplacian used by flow_residual().
    from scipy.sparse import coo_matrix,diags
    from scipy.sparse.linalg import splu
    s=p.Slime(geo,7)
    for _ in range(5):s.step()
    center=geo['city_xy'][0]+np.array([230.,30.])
    s.block(center,65.)
    C=np.where(s.alive,s.D/s.L,0.)
    I,J=s.I,s.J;n=s.n
    A=coo_matrix((np.r_[C,C],(np.r_[I,J],np.r_[J,I])),shape=(n,n)).tocsr()
    deg=np.asarray(A.sum(axis=1)).ravel()
    eps=1e-9*max(deg.max(),1e-12)
    L=(diags(deg+eps)-A).tocsc()
    b=np.zeros(n);src=int(s.city_node[0]);dst=int(s.city_node[1]);b[src]=5;b[dst]=-5
    v=splu(L).solve(b)
    q=C*(v[I]-v[J])
    net=np.bincount(I,weights=q,minlength=n)-np.bincount(J,weights=q,minlength=n)
    assert np.max(np.abs(net-b))<1e-3


def test_track_reader_ignores_missing_and_malformed_geometry(tmp_path):
    from research.compare_real_tracks import read_lines,sample_lines
    file=tmp_path/'mixed.geojson'
    file.write_text('''{"type":"FeatureCollection","features":[
      {"type":"Feature","geometry":null},
      {"type":"Feature","geometry":{"type":"Point","coordinates":[77,28]}},
      {"type":"Feature","geometry":{"type":"LineString","coordinates":[[77,23],[77.04,23.04]]}}
    ]}''')
    lines=list(read_lines(file))
    assert len(lines)==1
    pts,weights,km,count,rejected=sample_lines(lines)
    assert count==1 and rejected==0 and pts.shape[1]==2
