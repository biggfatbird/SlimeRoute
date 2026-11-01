"""High-resolution static visualizations of verified same-grid baselines."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from research.network_artifacts import load_masks, load_mask
import physarum_india as p

OUT=Path('out'); metrics=json.loads((OUT/'benchmark_metrics.json').read_text())
geo=p.build_geometry(); masks=load_masks(OUT/'baseline_masks.npz',geo)
names=['Physarum','terminal_MST_expanded','Delhi_shortest_path_union']
labels=['PHYSARUM-INSPIRED','EXPANDED TERMINAL MST','DELHI SHORTEST-PATH UNION']
colors=['#ffb72b','#64d5cf','#b78af7'];bg='#070a0f';fg='#edf2f7';mut='#a5b4c5'
plt.rcParams.update({'font.family':'DejaVu Sans','figure.facecolor':bg,'savefig.facecolor':bg,'axes.facecolor':bg,'text.color':fg,'axes.labelcolor':fg,'xtick.color':mut,'ytick.color':mut})
fig=plt.figure(figsize=(18,9),dpi=165,facecolor=bg)
fig.text(.045,.925,'THREE WAYS TO CONNECT 16 INDIAN CITIES',fontsize=25,fontweight='bold')
fig.text(.045,.88,'The same 25-km candidate lattice  |  Different design objectives  |  Seed 7',fontsize=13,color=mut)
for index,name in enumerate(names):
    ax=fig.add_axes([.03+index*.326,.20,.31,.62]);ax.set_aspect('equal');ax.axis('off')
    ax.set_xlim(*geo['xlim']);ax.set_ylim(*geo['ylim'])
    poly=geo['poly_xy'];ax.fill(poly[:,0],poly[:,1],color='#111c28',edgecolor='#314355',lw=.9)
    mask=masks[name];segments=np.stack([geo['pts'][geo['I'][mask]],geo['pts'][geo['J'][mask]]],axis=1)
    ax.add_collection(LineCollection(segments,colors=colors[index],linewidths=2.1,alpha=.91,capstyle='round'))
    xy=geo['city_xy'];ax.scatter(xy[:,0],xy[:,1],color=fg,s=10,zorder=5)
    m=metrics['unaffected'][name]
    x=.05+index*.326
    fig.text(x,.82,labels[index],fontsize=14,color=colors[index],fontweight='bold')
    fig.text(x,.15,f'{m["length_km_approx"]:,.0f} km',fontsize=20,fontweight='bold')
    fig.text(x,.105,f'{m["mean_detour_reachable_only"]:.2f}× mean detour   •   {m["connected_pairs"]}/120 connected',fontsize=11,color=mut)
fig.text(.046,.035,'MODELING NOTE   Hand-drawn boundary, approximate map distances and terrain costs. These are algorithmic designs, not observed rail tracks.',fontsize=10,color=mut)
fig.savefig(OUT/'algorithm_baselines.png',bbox_inches='tight',pad_inches=.25);plt.close(fig)

fig,ax=plt.subplots(figsize=(11,7),dpi=160)
fig.suptitle('NETWORK EFFICIENCY vs RESILIENCE',fontsize=21,fontweight='bold',x=.08,y=.97,ha='left')
ax.set_position([.13,.18,.8,.67]);ax.set_facecolor('#0f1924')
for i,name in enumerate(names):
    m=metrics['unaffected'][name];d=metrics['damage_summary'][name]
    ax.scatter(m['length_km_approx']/1000,m['mean_detour_reachable_only'],s=340,c=colors[i],edgecolors=fg,linewidths=.8,zorder=5)
    ax.annotate(labels[i]+f'\n{d["fraction_all_120_stay_connected"]:.0%} of 25 sites keep all links',
        (m['length_km_approx']/1000,m['mean_detour_reachable_only']),
        xytext=(15,14 if i!=1 else -34),textcoords='offset points',color=fg,fontsize=11)
ax.grid(color='#324353',alpha=.4);ax.set_axisbelow(True)
ax.set_xlabel('Total network length (thousands of approximate km)',fontsize=12,labelpad=14)
ax.set_ylabel('Mean route detour (lower is better)',fontsize=12,labelpad=14)
ax.set_xlim(4.5,17);ax.set_ylim(1.05,2.45)
fig.text(.095,.065,'Damage sites sampled from the union of networks; disruption = 150-km radius.\nDifferent network budgets — comparison is illustrative, not budget-matched.',fontsize=10,color=mut)
fig.savefig(OUT/'tradeoff.png',bbox_inches='tight',pad_inches=.3);plt.close(fig)
print('Wrote algorithm_baselines.png and tradeoff.png')
