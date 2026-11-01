"""Measured *spatial proximity* to a raster derived from mapped Indian railway LineStrings.

This is real rail *line geometry* downsampled to a 0.2-degree cell mask,
NOT a physical railway routing graph and not a high-precision map.
The source is datta07/INDIAN-SHAPEFILES, INDIA/INDIAN_RAILWAYS.geojson.
Proximity is evaluated using a local azimuthal equidistant projection.
"""
from pathlib import Path
import json,sys
import numpy as np
from scipy.spatial import cKDTree
from pyproj import CRS,Transformer,Geod
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research.network_artifacts import load_masks, load_mask
import physarum_india as p
from build_rail_raster import decode

SOURCE='https://github.com/datta07/INDIAN-SHAPEFILES/blob/master/INDIA/INDIAN_RAILWAYS.geojson'
SHA='63ff14b3f3b62a6d18d4950e9ab4ba99a3c5c16d'
MODEL_DIR=Path(__file__).resolve().parents[1]
PROJ=Transformer.from_crs('EPSG:4326',CRS.from_proj4('+proj=aeqd +lat_0=22 +lon_0=82 +datum=WGS84 +units=m +no_defs'),always_xy=True)
GEOD=Geod(ellps='WGS84')

def rail_points():
    bitmap=decode()
    yy,xx=np.nonzero(bitmap)
    ll=np.c_[68+xx*.2,8+yy*.2]
    return bitmap,ll,np.column_stack(PROJ.transform(ll[:,0],ll[:,1]))

def sample_model(geo,mask):
    # Sample selected model segments approximately every <=5km on their actual
    # WGS84 line geometry, with length weights in km.
    a=geo['pts'][geo['I'][mask]];b=geo['pts'][geo['J'][mask]]
    lon1,lat1=p.unproj(a[:,0],a[:,1]);lon2,lat2=p.unproj(b[:,0],b[:,1])
    _,_,dist=GEOD.inv(lon1,lat1,lon2,lat2);km=dist/1000
    xy=[]; weights=[]
    for xa,ya,xb,yb,L in zip(lon1,lat1,lon2,lat2,km):
        n=max(1,int(np.ceil(L/5)))
        t=(np.arange(n)+.5)/n
        xs,ys=PROJ.transform(xa+(xb-xa)*t,ya+(yb-ya)*t)
        xy.append(np.c_[xs,ys]);weights.append(np.full(n,L/n))
    return np.concatenate(xy),np.concatenate(weights)

def compare(geo,railmetric,mask,thresholds=(25,50,75,100)):
    sm,weights=sample_model(geo,mask)
    ds,_=cKDTree(railmetric).query(sm)
    dr,_=cKDTree(sm).query(railmetric)
    results={}
    for t in thresholds:
        results[str(t)]={'fraction_model_length_within_km_of_mapped_track_cells':float(weights[ds<=1000*t].sum()/weights.sum()),
                         'fraction_occupied_rail_cells_within_km_of_model':float(np.mean(dr<=1000*t))}
    return {'sampled_model_length_km':float(weights.sum()),'model_sample_count':len(weights),
            'median_model_point_to_railcell_km':float(np.median(ds)/1000),
            'median_railcell_to_model_km':float(np.median(dr)/1000),
            'thresholds':results}

def plot(geo,raster,modelmask,augmask,metrics,out):
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans'})
    fig=plt.figure(figsize=(10.8,13.5),dpi=150,facecolor='#080c12')
    fig.text(.06,.945,'SLIMEROUTE',fontsize=34,color='#f4f5f7',weight='bold')
    fig.text(.06,.918,'Bio-inspired network vs. mapped railway geometry',fontsize=14,color='#a6b6c6')
    fig.text(.06,.885,'REAL RAIL LINE DATA  /  SPATIAL COMPARISON',fontsize=12,color='#ffc34a',weight='bold')
    # This source covers thousands of nationwide railway cells. 50km proximity
    # saturates for most connecting networks, so do NOT headline it as similarity.
    s=metrics['networks']['Physarum']['thresholds']['25']
    t=metrics['networks']['Augmented_MST']['thresholds']['25']
    fig.text(.06,.850,'29,946',fontsize=31,color='#f6d36a',weight='bold')
    fig.text(.255,.850,'mapped railway-line features in source GIS',fontsize=12,color='#dce6ef')
    fig.text(.06,.824,f"25-km nearby: Physarum {s['fraction_model_length_within_km_of_mapped_track_cells']:.0%}  |  Graph heuristic {t['fraction_model_length_within_km_of_mapped_track_cells']:.0%}",fontsize=10.5,color='#b8c7d3')
    for i,(name,mask) in enumerate([('PHYSARUM-INSPIRED',modelmask),('GRAPH HEURISTIC',augmask)]):
        ax=fig.add_axes([.045+i*.50,.265,.475,.515]);ax.set_facecolor('#080c12');ax.axis('off')
        ax.set_xlim(67.3,98.6);ax.set_ylim(7.2,35.6);ax.set_aspect(1.25)
        # Source raster is an occupancy *derived from geospatial railway polylines*.
        ax.imshow(np.ma.masked_where(~raster,raster),extent=(67.9,97.9,7.9,34.5),origin='lower',cmap='Greys',interpolation='nearest',alpha=.85,vmin=0,vmax=1,aspect='auto',zorder=1)
        # plot occupied rail locations in blue-cyan for legibility on dark.
        yy,xx=np.nonzero(raster)
        ax.scatter(68+.2*xx,8+.2*yy,s=1.1,c='#4fa9c3',alpha=.60,linewidths=0,zorder=2,rasterized=True)
        a=geo['pts'][geo['I'][mask]];b=geo['pts'][geo['J'][mask]]
        x1,y1=p.unproj(a[:,0],a[:,1]);x2,y2=p.unproj(b[:,0],b[:,1])
        seg=np.stack([np.c_[x1,y1],np.c_[x2,y2]],axis=1)
        ax.add_collection(LineCollection(seg,colors='#ffc348' if i==0 else '#f28c66',linewidths=2.5,alpha=.92,zorder=4))
        lon,lat=p.unproj(geo['city_xy'][:,0],geo['city_xy'][:,1]);ax.scatter(lon,lat,c='#fcfaf4',s=16,edgecolor='#111a23',linewidth=.6,zorder=5)
        ax.set_title(name,fontsize=10.5,color='#edf2f7',weight='bold',pad=10)
    fig.text(.06,.245,'HOW TO READ THIS',fontsize=11,color='#ffc34a',weight='bold')
    fig.text(.06,.209,'Blue = mapped railway line cells   |   Yellow/orange = simulated/modelled network',color='#cad6e1',fontsize=11)
    fig.text(.06,.175,'Track geometry rasterized to 0.2° cells (~20 km). Proximity is approximate,',color='#97a8b9',fontsize=10)
    fig.text(.06,.155,'Neither network reproduces railway topology. Dense rail coverage can inflate proximity.',color='#97a8b9',fontsize=10)
    fig.text(.06,.116,'Source: datta07/INDIAN-SHAPEFILES  |  29,946 railway line features',color='#94a8b8',fontsize=10)
    fig.text(.06,.094,'Reproduced 2026-10-31  |  Research prototype, not a planning model',color='#7d92a4',fontsize=9)
    fig.savefig(out,facecolor=fig.get_facecolor());plt.close(fig)

if __name__=='__main__':
    geo=p.build_geometry();rail,lonlat,rmetric=rail_points()
    src=load_masks(MODEL_DIR/'out'/'baseline_masks.npz',geo)
    masks={'Physarum':src['Physarum'], 'Terminal_MST':src['terminal_MST_expanded'],
           'Delhi_shortest_path_union':src['Delhi_shortest_path_union'],
           'Augmented_MST':load_mask(MODEL_DIR/'out'/'augmented_mst_mask.npy',geo)}
    vals={key:compare(geo,rmetric,mask) for key,mask in masks.items()}
    data={'description':'Proximity between model lattice network and rasterized actual railway-line geometries (NOT railway route connectivity)',
          'source':SOURCE,'source_git_blob_sha':SHA,'railway_line_features_in_source':29946,
          'railway_coordinate_vertices_in_source':738962,'source_track_gauges_present':['BG','MG','MTG','NG'],
          'approx_raw_polyline_length_km_in_source':86355,
          'source_length_warning':'Polyline lengths can include duplicates and parallel tracks; not a verified Indian Railways route-km total.',
          'raster_grid':{'origin_lon':68,'origin_lat':8,'res_degrees':.2,'shape':[133,150], 'occupied_cells':int(rail.sum()),
                         'position_uncertainty':'Rounding to grid cells up to ~16 km; proximity measured to cell centers, not exact track polylines.'},
          'proximity_is_not':'proof of similar railway topology or routing performance',
          'network_comparison':'All models use same older approximate terrain and 16-city lattice; real rail mapping is independent. National railway tracks serve far more cities.',
          'networks':vals}
    out=MODEL_DIR/'out'/'railway_geometry_comparison.json';out.write_text(json.dumps(data,indent=2));
    plot(geo,rail,masks['Physarum'],masks['Augmented_MST'],data,MODEL_DIR/'out'/'real_rail_geometry_comparison.png')
    print(json.dumps({'rails_cells':int(rail.sum()),'network_50km':{k:v['thresholds']['50'] for k,v in vals.items()}},indent=2));print('saved',out)
