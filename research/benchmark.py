"""Reproducible grid-matched route-design baselines and Physarum failure studies.

All reference networks use the SAME candidate lattice as the slime model. They
are algorithmic baselines, not observed railway tracks. Distance is measured in
original model projection (approximate kilometres), not geodesic or surveyed km.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from collections import Counter
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import dijkstra, minimum_spanning_tree, connected_components
from scipy.spatial import cKDTree
import physarum_india as p


def candidate_graph(geo, active=None, weighted=True):
    I,J=geo['I'],geo['J']
    if active is None:active=np.ones(len(I),dtype=bool)
    w=geo['Lcost'] if weighted else geo['Lphys']
    a=sp.coo_matrix((w[active],(I[active],J[active])),shape=(len(geo['pts']),)*2).tocsr()
    return a+a.T


def reconstruct_edges(prev, start, goal, lookup, steps_limit):
    """Follow one SciPy Dijkstra predecessor array backwards."""
    node=int(goal); start=int(start); result=set()
    for _ in range(steps_limit):
        if node==start: return result
        parent=int(prev[node])
        if parent < 0: raise ValueError(f'unreachable {start}->{goal}')
        edge=(min(node,parent),max(node,parent))
        result.add(lookup[edge]);node=parent
    raise RuntimeError('predecessor loop')


def baselines(geo):
    """Metric-closure MST with expanded grid paths, and shortest-path tree from Delhi.

    The MST is a terminal *approximation*, not globally optimal Steiner tree.
    The SPT is rooted in Delhi, so differs in objective from the all-pairs model.
    """
    graph=candidate_graph(geo)
    nodes=geo['city_node']; n=len(geo['pts'])
    lookup={(min(int(a),int(b)),max(int(a),int(b))):k
            for k,(a,b) in enumerate(zip(geo['I'],geo['J']))}
    dist,prev=dijkstra(graph,directed=False,indices=nodes,return_predecessors=True)
    closure=dist[:,nodes]
    if not np.isfinite(closure).all():raise ValueError('unreachable terminal on candidate mesh')
    mst=minimum_spanning_tree(sp.csr_matrix(closure)).tocoo()
    metric_mask=np.zeros(len(geo['I']),bool)
    for s,t in zip(mst.row,mst.col):
        for edge in reconstruct_edges(prev[s],nodes[s],nodes[t],lookup,n): metric_mask[edge]=True
    star_mask=np.zeros(len(geo['I']),bool)
    for target in nodes:
        for edge in reconstruct_edges(prev[0],nodes[0],target,lookup,n):star_mask[edge]=True
    return {'terminal_MST_expanded':metric_mask,'Delhi_shortest_path_union':star_mask}


def network_metrics(geo,mask):
    I,J=geo['I'],geo['J'];n=len(geo['pts']);city=geo['city_node']
    w=geo['Lphys'][mask]; cost=geo['Lcost'][mask]
    g=sp.coo_matrix((w,(I[mask],J[mask])),shape=(n,n)).tocsr()
    dist=dijkstra(g,directed=False,indices=city)[:,city]
    c=geo['pts'][city]
    direct=np.linalg.norm(c[:,None,:]-c[None,:,:],axis=2)
    tri=np.triu_indices(len(city),1)
    d=dist[tri]; base=direct[tri]; good=np.isfinite(d)
    # Record detour over *reachable* pairs only, so cannot hide missing connections.
    return {'length_km_approx':float(w.sum()),
            'terrain_weighted_km_approx':float(cost.sum()),
            'edges':int(mask.sum()),
            'connected_pairs':int(good.sum()),'total_pairs':int(good.size),
            'mean_detour_reachable_only':float(np.mean(d[good]/base[good])) if good.any() else None,
            'max_detour_reachable_only':float(np.max(d[good]/base[good])) if good.any() else None}


def city_pair_mask(geo, D, alive,threshold):
    if not np.any(alive):return np.zeros_like(alive)
    return alive & (D > threshold * D[alive].max())


def blocked_mask(geo,center,radius):
    pt=geo['pts'];inside=np.linalg.norm(pt-center,axis=1)<radius
    return ~(inside[geo['I']] | inside[geo['J']])


def sample_damage_centers(geo,mask,radius,n=20,seed=111):
    """Sample from the union of networks, with spatial separation, no survival filter.

    This sampling is conditioned on having *some* route in the area, not on
    a particular model surviving the damage. Do not extrapolate it to all India.
    """
    mids=(geo['pts'][geo['I']] + geo['pts'][geo['J']])/2
    city=geo['city_xy']
    usable=np.where(mask & (np.min(np.linalg.norm(mids[:,None,:]-city[None,:,:],axis=2),axis=1)>radius+35))[0]
    if not len(usable):raise RuntimeError('No eligible damage sites')
    rng=np.random.default_rng(seed)
    order=rng.permutation(usable)
    chosen=[]
    for edge in order:
        c=mids[edge]
        if all(np.linalg.norm(c-p)>max(65.,radius*0.75) for p in chosen):
            chosen.append(c)
        if len(chosen)>=n:break
    if len(chosen)<n:raise RuntimeError(f"Only {len(chosen)} distinct damage sites found")
    return np.asarray(chosen)


def damage_sweep(geo,models,centers,radius):
    rows=[]
    for ci,center in enumerate(centers):
        keep=blocked_mask(geo,center,radius)
        for model,initial in models.items():
            metrics=network_metrics(geo,initial & keep)
            rows.append({'location':ci, 'lon':float(p.unproj(center[0],center[1])[0]),
                         'lat':float(p.unproj(center[0],center[1])[1]),
                         'model':model, **metrics})
    return rows


def flow_residual(geo,sl,seed=19):
    """Small physically grounded Kirchhoff test with exact ground gauge.
    Solves the original live graph with a fixed node (no diagonal leakage),
    then validates global current conservation and Ohmic flow on every edge.
    """
    rng=np.random.default_rng(seed)
    I,J=geo['I'],geo['J'];n=sl.n
    C=np.where(sl.alive,sl.D/sl.L,0.)
    lap=sp.coo_matrix((np.r_[C,-C,-C,C],
      (np.r_[I,I,J,J],np.r_[I,J,I,J])),shape=(n,n)).tocsr()
    source=int(sl.city_node[0]);sink=int(sl.city_node[1]); b=np.zeros(n)
    b[source]=5.;b[sink]=-5.
    # For post-disruption disconnected grid, use pre-damage graph for this check.
    from scipy.sparse.linalg import spsolve
    x=spsolve(lap[:-1,:-1].tocsc(),b[:-1]); potential=np.r_[x,0.]
    flux=C*(potential[I]-potential[J]); net=np.bincount(I,weights=flux,minlength=n)-np.bincount(J,weights=flux,minlength=n)
    return {'max_nodal_flux_error':float(np.max(abs(net-b))),
            'relative_flux_error':float(np.linalg.norm(net-b)/np.linalg.norm(b))}


def run(output,quick=False,seed=7,n_damage=20):
    geo=p.build_geometry();model=p.Slime(geo,seed)
    steps=140 if quick else p.T_GROW
    for k in range(steps):model.step()
    end_alive=model.alive.copy()
    m=city_pair_mask(geo,model.D,end_alive,p.REL_THR)
    base=baselines(geo)
    nets={'Physarum':m,**base}
    all_metrics={name:network_metrics(geo,mm) for name,mm in nets.items()}
    numerics=flow_residual(geo,model)
    centers=sample_damage_centers(geo,np.logical_or.reduce(list(nets.values())),p.BLOCK_R,n_damage)
    damage=damage_sweep(geo,nets,centers,p.BLOCK_R)
    # Evaluate counts with all damages, including failures that disconnect the graph.
    summary={}
    for name in nets:
        vals=[row for row in damage if row['model']==name]
        summary[name]={
          'locations':len(vals),
          'mean_connected_pairs':float(np.mean([v['connected_pairs'] for v in vals])),
          'min_connected_pairs':int(min(v['connected_pairs'] for v in vals)),
          'fraction_all_120_stay_connected':float(np.mean([v['connected_pairs']==120 for v in vals])),
        }
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    with open(output/'benchmark_metrics.json','w') as f:
        json.dump({'method':'same lattice, original approximate km, weighted cost controls shortest-path choices',
                   'seed':seed,'growth_steps':steps,'damage_radius_km':p.BLOCK_R,
                   'damage_location_selection':'random spatially separated centers on union of three network edge sets, outside radius+35 km of any city; no connectivity filtering',
                   'unaffected':all_metrics,'flow_conservation':numerics,
                   'damage_summary':summary},f,indent=2)
    with open(output/'damage_locations.csv','w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(damage[0]));writer.writeheader();writer.writerows(damage)
    from research.network_artifacts import save_masks
    save_masks(output/'baseline_masks.npz',geo,**nets)
    return all_metrics,numerics,summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='out');parser.add_argument('--seed',type=int,default=7)
    parser.add_argument('--quick',action='store_true');parser.add_argument('--damage-sites',type=int,default=20)
    args=parser.parse_args();a,b,c=run(args.out,args.quick,args.seed,args.damage_sites)
    print(json.dumps({'unaffected':a,'flow_conservation':b,'damage_summary':c},indent=2))
