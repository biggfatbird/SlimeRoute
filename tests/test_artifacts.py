import numpy as np
import pytest
from research.network_artifacts import save_masks, load_masks
from research.resilience_study import survival
from research.benchmark import network_metrics, blocked_mask
import physarum_india as p


def test_mask_remaps_when_edge_order_changes(tmp_path):
    geo = dict(pts=np.array([[0., 0.], [1., 0.], [2., 0.]]), I=np.array([0, 1]), J=np.array([1, 2]))
    path = tmp_path / 'm.npz'
    save_masks(path, geo, route=np.array([True, False]))
    reordered = dict(geo, I=geo['I'][::-1], J=geo['J'][::-1])
    assert load_masks(path, reordered)['route'].tolist() == [False, True]
    wrong = dict(geo, pts=geo['pts'] + 1)
    with pytest.raises(ValueError, match='coordinates'):
        load_masks(path, wrong)


def test_missing_identity_and_modified_mask_fail_closed(tmp_path):
    geo = dict(pts=np.array([[0., 0.], [1., 0.]]), I=np.array([0]), J=np.array([1]))
    path = tmp_path / 'm.npy'
    np.save(path, np.array([True]))
    with pytest.raises(ValueError, match='Missing edge identity'):
        load_masks(path, geo)
    save_masks(path, geo, mask=np.array([True]))
    np.save(path, np.array([False]))
    with pytest.raises(ValueError, match='checksum'):
        load_masks(path, geo)


def test_geometry_canonical_under_permuted_spatial_tree(monkeypatch):
    original = p.cKDTree
    expected = p.build_geometry()
    class ReorderedTree:
        def __init__(self, *args, **kw): self.tree = original(*args, **kw)
        def query_pairs(self, *args, **kw): return self.tree.query_pairs(*args, **kw)[::-1]
        def query(self, *args, **kw): return self.tree.query(*args, **kw)
    monkeypatch.setattr(p, 'cKDTree', ReorderedTree)
    fresh = p.build_geometry()
    assert np.array_equal(expected['I'], fresh['I'])
    assert np.array_equal(expected['J'], fresh['J'])


def test_connectivity_counter_agrees_with_shortest_path_metrics():
    geo = p.build_geometry()
    mask = np.ones(len(geo['I']), bool)
    centers = geo['city_xy'][[0, 5, 10]]
    counts = survival(geo, mask, centers, 150)
    expected = [network_metrics(geo, mask & blocked_mask(geo,c,150))['connected_pairs'] for c in centers]
    assert counts.tolist() == expected
