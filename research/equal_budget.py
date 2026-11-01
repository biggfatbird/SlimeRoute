"""Heuristic route-improvement baseline starting from terminal MST, at slime network's length budget.

This is an explicit heuristic, NOT an optimal equal-budget network design.
"""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.sparse.csgraph import dijkstra
from research.benchmark import candidate_graph,baselines,reconstruct_edges,network_metrics
import physarum_india as p

def augmented_tree(geo,budget_km):
    masks=baselines(geo);start=masks['terminal_MST_expanded'].copy()
    assert geo['Lphys'][start].sum() <= budget_km
    nodes=geo['city_node'];n=len(geo['pts']);full=candidate_graph(geo)
    full_dist,full_prev=dijkstra(full,directed=False,indices=nodes,return_predecessors=True)
    lookup={(min(int(a),int(b)),max(int(a),int(b))):k for k,(a,b) in enumerate(zip(geo['I'],geo['J']))}
    candidates=[]
    for i in range(len(nodes)):
        for j in range(i+1,len(nodes)):
            path=np.array(sorted(reconstruct_edges(full_prev[i],nodes[i],nodes[j],lookup,n)),dtype=int)
            candidates.append((i,j,path))
    additions=[]
    for k in range(120):
        remain=budget_km-geo['Lphys'][start].sum()
        if remain<min(geo['Lphys']):break
        current_graph=candidate_graph(geo,start,weighted=True)  # same terrain-adjusted objective as full_dist
        D=dijkstra(current_graph,directed=False,indices=nodes)[:,nodes]
        best=None
        for i,j,path in candidates:
            new=path[~start[path]]
            if not len(new):continue
            added=geo['Lphys'][new].sum()
            if added>remain+1e-9:continue
            potential=full_dist[i,nodes[j]]
            gap=max(0,D[i,j]-potential)
            # Consistent terrain-weighted route-cost relief per physical km of new track.
            # Physical construction length is used only for the network budget.
            score=gap/added
            if best is None or score>best[0]:best=(score,i,j,new,float(added))
        if best is None or best[0]<=1e-7:break
        _,i,j,new,added=best
        start[new]=True
        additions.append({'from':geo['names'][i],'to':geo['names'][j],'added_km':added})
    return start,additions

if __name__=='__main__':
    import argparse
    pa=argparse.ArgumentParser();pa.add_argument('--budget-km',type=float,default=10034.549882328189);pa.add_argument('--out',default='out')
    a=pa.parse_args();geo=p.build_geometry();mask,add=augmented_tree(geo,a.budget_km);m=network_metrics(geo,mask)
    print(json.dumps({'metrics':m,'additions':add},indent=2))
    from research.network_artifacts import save_masks
    save_masks(Path(a.out)/'augmented_mst_mask.npy',geo,mask=mask)
    (Path(a.out)/'augmented_mst_metrics.json').write_text(json.dumps({'budget_km':a.budget_km,'metrics':m,'additions':add,'description':'greedy reduction of terrain-weighted all-pairs route cost, physical-length budget, same lattice, nonoptimal heuristic'},indent=2))
