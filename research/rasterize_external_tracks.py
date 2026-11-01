"""Recompute the 0.2-degree rail occupancy raster from ORIGINAL mapped railway GeoJSON.

Input is trusted as data only (JSON; never executes downloaded code). For a known
source snapshot run `python research/download_real_tracks.py` first.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

ORIGIN_LON=68.0; ORIGIN_LAT=8.0; RES_DEG=0.2
WIDTH=150; HEIGHT=133
SAMPLING_STEP_DEG=0.08


def rasterize_lines(lines):
    raster=np.zeros((HEIGHT,WIDTH),dtype=np.bool_)
    accepted=0; bad=0; vertices=0
    for coords in lines:
        try:
            arr=np.asarray(coords,dtype=float)
        except (ValueError,TypeError):
            bad+=1;continue
        if arr.ndim!=2 or arr.shape[1]<2 or len(arr)<2 or not np.isfinite(arr[:,:2]).all():
            bad+=1;continue
        arr=arr[:,:2]; accepted+=1;vertices+=len(arr)
        a,b=arr[:-1],arr[1:]
        n=np.maximum(1,np.ceil(np.linalg.norm(b-a,axis=1)/SAMPLING_STEP_DEG).astype(int))
        # Include both segment endpoints, as in the source-geometry inspection.
        sizes=n+1
        ids=np.repeat(np.arange(len(n)),sizes)
        base=np.repeat(np.cumsum(sizes)-sizes,sizes)
        t=(np.arange(len(ids))-base)/np.repeat(n,sizes)
        positions=a[ids]+(b[ids]-a[ids])*t[:,None]
        x=np.floor((positions[:,0]-ORIGIN_LON)/RES_DEG+.5).astype(int)
        y=np.floor((positions[:,1]-ORIGIN_LAT)/RES_DEG+.5).astype(int)
        valid=(x>=0)&(x<WIDTH)&(y>=0)&(y<HEIGHT)
        raster[y[valid],x[valid]]=True
    return raster,{'accepted_lines':accepted,'rejected_lines':bad,'coordinate_vertices':vertices,
                   'occupied_cells':int(raster.sum())}


def geojson_lines(data):
    features=data.get('features',[data])
    for f in features:
        g=f.get('geometry',f)
        if not isinstance(g,dict):continue
        if g.get('type')=='LineString':yield g.get('coordinates',[])
        elif g.get('type')=='MultiLineString':yield from g.get('coordinates',[])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--tracks',default='data/INDIAN_RAILWAYS.geojson')
    parser.add_argument('--verify',action='store_true',help='assert raster equals bundled snapshot')
    parser.add_argument('--out',default='data/rail_lines_raster_0p2deg_recomputed.npy')
    args=parser.parse_args()
    data=json.loads(Path(args.tracks).read_text(encoding='utf8'))
    grid,stats=rasterize_lines(geojson_lines(data))
    if args.verify:
        from build_rail_raster import decode
        assert np.array_equal(grid,decode()),'Full-geometry raster differs from published source snapshot; inspect data/sampling assumptions.'
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    np.save(args.out,grid)
    print(json.dumps(stats,indent=2))
    print('Saved',args.out)

if __name__=='__main__':main()
