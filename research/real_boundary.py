"""Optional use of a supplied genuine boundary polygon for *new* model runs.

IMPORTANT: Changing the boundary changes the candidate graph, so none of the
provided seed-7 benchmark numbers are valid for this new geometry.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import physarum_india as p

def polygon_rings(obj):
    geometry=obj.get('geometry',obj)
    t=geometry.get('type');c=geometry.get('coordinates')
    if t=='Polygon':return [c[0]]
    if t=='MultiPolygon':return [part[0] for part in c]
    return []

def load_mainland(path):
    """Largest exterior ring by signed planar area; assumes EPSG:4326.

    Only a MAINLAND ring is used for the model candidate grid. Offshore islands
    are excluded. No attempt is made to settle disputed political boundaries.
    """
    obj=json.loads(Path(path).read_text())
    feats=obj['features'] if obj.get('type')=='FeatureCollection' else [obj]
    rings=[]
    for ft in feats:
        for ring in polygon_rings(ft):
            ar=np.asarray(ring,dtype=float)
            if ar.ndim!=2 or len(ar)<4 or ar.shape[1]<2:continue
            if np.any(~np.isfinite(ar[:,:2])):continue
            x,y=ar[:,0],ar[:,1]
            area=abs(float(np.dot(x,np.roll(y,-1))-np.dot(y,np.roll(x,-1))))/2
            rings.append((area,ar[:,:2]))
    if not rings:raise ValueError('Expected GeoJSON Polygon/MultiPolygon (not LineString); no valid polygons found')
    _,ring=max(rings,key=lambda x:x[0])
    return ring

def build_geometry_with_real_boundary(path):
    ring=load_mainland(path)
    old=p.INDIA
    try:
        p.INDIA=[tuple(x) for x in ring]
        geo=p.build_geometry()
    finally:
        p.INDIA=old
    return geo

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--geojson',required=True);ap.add_argument('--seed',type=int,default=7)
    a=ap.parse_args();geo=build_geometry_with_real_boundary(a.geojson)
    s=p.Slime(geo,a.seed)
    for _ in range(p.T_GROW):s.step()
    r=p.analyse(geo,s.D,s.alive)
    print(json.dumps({'provenance':a.geojson,'model_changed':True,'nodes':len(geo['pts']),
      'edges':len(geo['I']),'network_length_km_approx':r['total_km'],
      'connected_city_pairs':r['connected_pairs'],'mean_detour_reachable_only':r['detour'],
      'WARNING':'Not directly comparable to other results, unless baselines are rerun on this new grid.'},indent=2))
