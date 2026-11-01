"""Portrait four-way research figure for LinkedIn carousel."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from research.network_artifacts import load_masks, load_mask
import physarum_india as p
D=Path('out');g=p.build_geometry();b=load_masks(D/'baseline_masks.npz',g);a=load_mask(D/'augmented_mst_mask.npy',g);m=json.loads((D/'benchmark_metrics.json').read_text())
M={'Physarum':b['Physarum'],'MST':b['terminal_MST_expanded'],'Delhi shortest-path union':b['Delhi_shortest_path_union'],'Augmented MST':a}
C=['#f3ae33','#58bcd1','#a889ed','#a5e37b']
plt.rcParams.update({'font.family':'DejaVu Sans','figure.facecolor':'#070a0f','savefig.facecolor':'#070a0f','text.color':'#edf2f7'})
f=plt.figure(figsize=(10,12.5),dpi=170)
f.text(.06,.958,'SLIME MOLD vs. GRAPH ALGORITHMS',fontsize=22,weight='bold')
f.text(.06,.923,'16 Indian cities  |  Same candidate grid  |  Seed 7',fontsize=12,color='#94a9bf')
for k,(name,mask) in enumerate(M.items()):
    row=k//2;col=k%2;left=.045+col*.495;bottom=.515-row*.42
    ax=f.add_axes([left,bottom,.47,.36]);ax.axis('off');ax.set_aspect('equal');ax.set_xlim(*g['xlim']);ax.set_ylim(*g['ylim'])
    poly=g['poly_xy'];ax.fill(poly[:,0],poly[:,1],color='#101a24',edgecolor='#314355',lw=.7)
    edges=np.stack((g['pts'][g['I'][mask]],g['pts'][g['J'][mask]]),axis=1)
    ax.add_collection(LineCollection(edges,colors=C[k],linewidths=1.6,alpha=.95,zorder=4,capstyle='round'))
    x=g['city_xy'];ax.scatter(x[:,0],x[:,1],s=6,color='white',zorder=5)
    if k==3:
        s=json.loads((D/'augmented_mst_metrics.json').read_text())['metrics']
    else:s=m['unaffected'][name if k==0 else ('terminal_MST_expanded' if k==1 else 'Delhi_shortest_path_union')]
    y=.876-row*.42
    f.text(left+.02,y,name.upper(),fontsize=14,color=C[k],weight='bold')
    f.text(left+.02,y-.345,f'{s["length_km_approx"]:,.0f} km   /   {s["mean_detour_reachable_only"]:.2f}× detour',fontsize=13,weight='bold')
f.text(.06,.055,'FINDING: THE PHYSARUM MODEL DOES NOT DOMINATE',fontsize=15,color='#f3ae33',weight='bold')
f.text(.06,.033,'The augmented MST achieves shorter routes at similar modeled length.',fontsize=11,color='#edf2f7')
f.text(.06,.011,'Illustrative geography and synthetic terrain, NOT actual railway tracks.',fontsize=9,color='#9cafc3')
f.savefig(D/'fourway_comparison.png',bbox_inches='tight',pad_inches=.1)
print('out/fourway_comparison.png written')
