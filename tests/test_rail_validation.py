import numpy as np
import pytest
from research.fullres_rail_analysis import verify_source, rail_topology


def test_rail_source_rejects_unverified_input(tmp_path):
    p=tmp_path/'source.json';p.write_text('{}')
    with pytest.raises(ValueError,match='hash mismatch'): verify_source(p)


def test_terminal_access_legs_are_included():
    V=np.array([[0.,0.],[10.,0.]])
    cities=np.array([[0.,1.],[10.,1.]])
    result=rail_topology(V,np.array([0]),np.array([2]),cities,stitch_km=.1)
    assert result['mean_detour']==pytest.approx(1.2)
