"""Fast sanity tests, distinct from an independent scientific validation."""
import numpy as np
import pytest
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from physarum_india import (build_geometry, Slime, cost_field, proj, unproj,
                            analyse_schematic, net_mask, K_PAIRS)

@pytest.fixture(scope='module')
def geo():
    return build_geometry()


def test_projection_round_trip():
    lon, lat = np.array([77.1, 88.36, 72.88]), np.array([28.61, 22.57, 19.08])
    x, y = proj(lon, lat)
    a, b = unproj(x, y)
    assert np.allclose(lon, a)
    assert np.allclose(lat, b)


def test_geometry_properties(geo):
    assert len(geo['names']) == len(set(geo['names'])) == 16
    assert len(set(geo['city_node'])) == 16
    assert len(geo['pts']) > 3000
    assert len(geo['I']) > len(geo['pts'])
    assert (geo['Lphys'] > 0).all()
    assert (geo['Lcost'] >= geo['Lphys']).all()
    assert (np.linalg.norm(geo['pts'][geo['city_node']] - geo['city_xy'], axis=1) < 25).all()


def test_city_pairs_on_raw_mesh_connected(geo):
    g = coo_matrix((np.ones(len(geo['I'])), (geo['I'], geo['J'])), shape=(len(geo['pts']),)*2)
    _, labels = connected_components(g, directed=False)
    assert len(set(labels[geo['city_node']])) == 1


def test_growth_step_deterministic(geo):
    a, b = Slime(geo, 17), Slime(geo, 17)
    for _ in range(3):
        a.step(); b.step()
    assert np.all(np.isfinite(a.D))
    assert (a.D > 0).all()
    assert np.array_equal(a.D, b.D)
    assert np.std(a.D) > 0


def test_schematic_connected(geo):
    result = analyse_schematic(geo)
    assert result['pairs'] == 120
    assert result['connected_pairs'] == 120
    assert result['detour'] > 1


def test_block_remove_edge(geo):
    s = Slime(geo, 7)
    city = geo['city_xy'][0]
    radius = 50.
    expected = (np.linalg.norm(geo['pts'] - city, axis=1) < radius)
    s.block(city, radius)
    assert not s.alive[(expected[geo['I']] | expected[geo['J']])].any()
    assert np.all(s.D[~s.alive] == 0.)
