"""Tests for the v5 full-resolution rail analysis and resilience sampling (toy geometries with known answers)."""
import numpy as np
import pytest

import physarum_india as p
from research import fullres_rail_analysis as fr
from research.resilience_study import sample_sites


def _flatten(lines_km):
    lens = np.array([len(a) for a in lines_km])
    return np.vstack(lines_km), np.r_[0, np.cumsum(lens)[:-1]], lens


def test_sample_segments_weights_sum_to_length():
    V = np.array([[0., 0.], [10., 0.], [10., 7.]])
    pts, w = fr.sample_segments(V, np.array([0, 1]), np.array([1, 2]), step=3.0)
    assert w.sum() == pytest.approx(17.0)
    assert len(pts) == 4 + 3                     # ceil(10/3) + ceil(7/3)


def test_straight_rail_has_detour_one():
    V, start, lens = _flatten([np.array([[0., 0.], [5., 0.]]), np.array([[5., 0.], [10., 0.]])])
    topo = fr.rail_topology(V, start, lens, np.array([[0., 0.], [10., 0.]]))
    assert topo["pairs_connected"] == 1
    assert topo["mean_detour"] == pytest.approx(1.0)


def test_bent_rail_detour_matches_geometry():
    # two cities 10 km apart joined by a V-shaped line: path = 2*sqrt(50)
    V, start, lens = _flatten([np.array([[0., 0.], [5., 5.]]), np.array([[5., 5.], [10., 0.]])])
    topo = fr.rail_topology(V, start, lens, np.array([[0., 0.], [10., 0.]]))
    assert topo["mean_detour"] == pytest.approx(2 * np.sqrt(50) / 10)


def test_stitching_tolerance_controls_connectivity():
    lines = [np.array([[0., 0.], [5., 0.]]), np.array([[5.3, 0.], [10., 0.]])]     # 0.3 km gap
    V, start, lens = _flatten(lines)
    cities = np.array([[0., 0.], [10., 0.]])
    assert fr.rail_topology(V, start, lens, cities, stitch_km=0.6)["pairs_connected"] == 1
    assert fr.rail_topology(V, start, lens, cities, stitch_km=0.1)["pairs_connected"] == 0


def test_simplified_roundtrip(tmp_path):
    pytest.importorskip("shapely")
    lines = [np.array([[77.0, 28.0], [77.5, 28.2], [78.0, 28.0]]), np.array([[80.0, 20.0], [80.1, 20.1]])]
    path = tmp_path / "rail.npz"
    fr.save_simplified(lines, path, tol_deg=0.0001)
    back = fr.load_simplified(path)
    assert len(back) == 2
    assert np.allclose(back[1], lines[1], atol=1e-4)


def test_proximity_of_a_network_to_itself_is_total():
    geo = p.build_geometry()
    mask = np.zeros(len(geo["I"]), bool)
    mask[:200] = True
    pts, w = fr.model_samples(geo, mask)
    prox = fr.proximity(pts, w, geo, mask)
    assert prox["model_length_within"]["5"] == pytest.approx(1.0)
    assert prox["rail_length_within_model"]["5"] == pytest.approx(1.0)


@pytest.mark.parametrize("radius", [100, 150, 200])
def test_resilience_sites_stay_away_from_cities(radius):
    geo = p.build_geometry()
    sites = sample_sites(geo, radius, n=50)
    d = np.linalg.norm(sites[:, None, :] - geo["city_xy"][None, :, :], axis=2).min(axis=1)
    assert len(sites) == 50 and d.min() > radius + 35
