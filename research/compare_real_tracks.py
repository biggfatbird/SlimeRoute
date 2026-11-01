"""Optional measured-geometry spatial comparison, NOT an inferred railway route graph.

Accepts external GeoJSON / GeoJSONL of actual *railway track polylines*.
No station-stop joins or invented straight rail segments. No public data is bundled.

Required extra dependencies: pyproj, shapely (for geodesic math only pyproj used).
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import numpy as np
from scipy.spatial import cKDTree
from pyproj import Geod, Transformer, CRS
import physarum_india as p

CRS_LOCAL=CRS.from_proj4('+proj=aeqd +lat_0=22 +lon_0=82 +datum=WGS84 +units=m +no_defs')
TRANSFORM=Transformer.from_crs('EPSG:4326',CRS_LOCAL,always_xy=True)
GEOD=Geod(ellps='WGS84')

def feature_lines(feature):
    """Extract LineString coordinates, safely ignoring null/invalid geometries."""
    if not isinstance(feature,dict):return []
    geometry=feature.get('geometry',feature)
    if not isinstance(geometry,dict):return []
    kind=geometry.get('type');coords=geometry.get('coordinates')
    if kind=='LineString':return [coords] if isinstance(coords,list) else []
    if kind=='MultiLineString':return [x for x in coords if isinstance(x,list)] if isinstance(coords,list) else []
    if kind=='GeometryCollection':
        out=[]
        for g in geometry.get('geometries',[]):out+=feature_lines(g)
        return out
    return []


def read_lines(path):
    path=Path(path)
    with path.open(encoding='utf-8') as stream:
        if path.suffix.lower() in {'.jsonl','.geojsonl','.ndjson'}:
            for line in stream:
                if line.strip():
                    for coords in feature_lines(json.loads(line)):yield coords
        else:
            data=json.load(stream)
            features=data.get('features',[data]) if data.get('type')=='FeatureCollection' else [data]
            for feature in features:
                for coords in feature_lines(feature):yield coords


def segments_from_lonlat(line):
    try:arr=np.asarray(line,dtype=float)
    except (TypeError,ValueError):return []
    if arr.ndim!=2 or arr.shape[0]<2 or arr.shape[1]<2:return []
    arr=arr[:,:2]
    if not np.isfinite(arr).all():return []
    # Strict India-relevant rough bounds for sanity; datasets may contain border branches.
    valid=(arr[:,0]>=66)&(arr[:,0]<=99)&(arr[:,1]>=6)&(arr[:,1]<=38)
    if not valid.all():return []
    return arr


def sample_lines(lines,spacing_km=5.0,max_samples=3_000_000):
    """Sample physical track polylines at <= spacing; returns AEQD metres +
    a per-sample km weight (within original polyline, approximate distance
    weighting). Endpoints don't count double between segments except zero weight.
    """
    points=[];weights=[];total=0.;count=0;rejected=0;nsamples=0
    for l in lines:
        arr=segments_from_lonlat(l)
        if len(arr)==0:rejected+=1;continue
        count+=1
        for a,b in zip(arr[:-1],arr[1:]):
            _,_,dist=GEOD.inv(a[0],a[1],b[0],b[1]);km=dist/1000
            if km <= 0:continue
            if km>250: # Straight segments this long are almost certainly train stops, not tracks.
                raise ValueError(f'Unusually long {km:.0f}-km segment in input. Likely a train-stop route, NOT physical track geometry.')
            num=max(1,int(math.ceil(km/spacing_km)))
            t=(np.arange(num)+.5)/num
            lon=a[0]+(b[0]-a[0])*t;lat=a[1]+(b[1]-a[1])*t
            x,y=TRANSFORM.transform(lon,lat)
            points.append(np.c_[x,y]);weights.append(np.full(num,km/num));total+=km;nsamples+=num
            if nsamples>max_samples:raise ValueError('Sampling limit hit; increase --spacing-km or filter railway categories')
    if not points:raise ValueError('No valid railway line geometry found')
    return np.vstack(points),np.concatenate(weights),total,count,rejected


def sample_slime(geo,mask,spacing_km=5.0):
    # Convert model grid edges -> geographic coordinates -> AEQD metric points.
    P=geo['pts'];I,J=geo['I'][mask],geo['J'][mask];pts=[];weights=[]
    for a,b in zip(P[I],P[J]):
        lon1,lat1=p.unproj(a[0],a[1]);lon2,lat2=p.unproj(b[0],b[1])
        _,_,length=GEOD.inv(lon1,lat1,lon2,lat2);km=length/1000
        nn=max(1,int(math.ceil(km/spacing_km)))
        t=(np.arange(nn)+.5)/nn
        lon=lon1+(lon2-lon1)*t;lat=lat1+(lat2-lat1)*t
        x,y=TRANSFORM.transform(lon,lat)
        pts.append(np.c_[x,y]);weights.append(np.full(nn,km/nn))
    return np.vstack(pts),np.concatenate(weights)


def weighted_near(reference,points,weights,tolerance_km):
    distance,_=cKDTree(reference).query(points)
    return float(weights[distance<=tolerance_km*1000].sum()/weights.sum()),float(np.quantile(distance/1000,.5))


def compare(geo,sim_mask,track_geojson,tolerance_km=50,spacing_km=5):
    tracks,weights,track_km,features,skipped=sample_lines(read_lines(track_geojson),spacing_km)
    sim,sw=sample_slime(geo,sim_mask,spacing_km)
    slime_near_rail,slime_median=weighted_near(tracks,sim,sw,tolerance_km)
    rail_near_slime,rail_median=weighted_near(sim,tracks,weights,tolerance_km)
    return {
      'data_file':str(track_geojson),'railway_features_accepted':features,
      'features_skipped_outside_india_or_bad':skipped,
      'rail_length_km_geodesic_raw':track_km,
      'CAUTION':'Rail track length may double-count parallel and overlapping lines, and coverage is countrywide, not route-pair matched.',
      'simulated_network_length_km_geodesic_approx':float(sw.sum()),
      'tolerance_km':tolerance_km,'spacing_km':spacing_km,
      'fraction_simulated_length_near_rail':slime_near_rail,
      'fraction_rail_length_near_simulated_network':rail_near_slime,
      'median_sample_distance_sim_to_rail_km':slime_median,
      'median_sample_distance_rail_to_sim_km':rail_median,
      'length_weighted':True,'geography':'WGS84 geodesic segment lengths; AEQD approximate spatial nearest-neighbour proximity',
      'limitations':'Proximity is not graph equivalence, route performance, or verified ability to construct new tracks.'
    }

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--tracks',required=True);ap.add_argument('--out',default='out/rail_comparison.json')
    ap.add_argument('--spacing-km',type=float,default=5);ap.add_argument('--tolerance-km',type=float,default=50)
    ap.add_argument('--seed',type=int,default=7); args=ap.parse_args()
    g=p.build_geometry();m=p.Slime(g,args.seed)
    for _ in range(p.T_GROW):m.step()
    comparison=compare(g,p.net_mask(m.D,m.alive),args.tracks,args.tolerance_km,args.spacing_km)
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(comparison,indent=2))
    print(json.dumps(comparison,indent=2))
