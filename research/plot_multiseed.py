import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=json.load(open('out/multi_seed_study.json'))['entries']
seeds=[x['seed'] for x in D]; det=[x['no_damage']['mean_detour_reachable_only'] for x in D];
frac=[x['fraction_fully_connected'] for x in D]; km=[x['no_damage']['length_km_approx'] for x in D]
bg='#070a0f'; txt='#f0f3f8';mut='#9bb0c5'; yellow='#ffb52c';cyan='#6ed0cc'
plt.rcParams.update({'figure.facecolor':bg,'savefig.facecolor':bg,'axes.facecolor':'#121c28','text.color':txt,'axes.labelcolor':txt,'ytick.color':mut,'xtick.color':mut})
f,(a,b)=plt.subplots(2,1,figsize=(10,11),dpi=165)
f.subplots_adjust(left=.13,right=.95,top=.83,bottom=.13,hspace=.36)
f.suptitle('CAN THE RESULT SURVIVE DIFFERENT RANDOM SEEDS?',fontsize=22,fontweight='bold',x=.10,y=.94,ha='left')
f.text(.10,.89,'10 full-growth simulations. Same parameters. Fixed 25 damage locations.',fontsize=12,color=mut)
a.bar([str(s) for s in seeds],det,color=yellow,width=.75);a.set_ylim(1,1.55);a.set_ylabel('Mean detour (×)',fontsize=12);a.set_xlabel('Random seed',fontsize=11)
a.axhline(np.mean(det),color='#f1f5fc',ls='--',alpha=.65,lw=1)
a.text(0.98,.95,f'Average {np.mean(det):.3f}×',transform=a.transAxes,ha='right',va='top',fontsize=11,color=txt)
b.bar([str(s) for s in seeds],np.array(frac)*100,color=cyan,width=.75)
b.set_ylim(0,105);b.set_ylabel('Damage sites preserving all 120 city connections (%)',fontsize=11)
b.set_xlabel('Random seed',fontsize=11)
b.axhline(np.mean(frac)*100,color='#f1f5fc',ls='--',alpha=.65,lw=1)
b.text(0.98,.94,f'Average {np.mean(frac):.0%}',transform=b.transAxes,ha='right',va='top',fontsize=11,color=txt)
for ax in (a,b):
 ax.spines[['top','right']].set_visible(False)
 ax.grid(axis='y',color='#435567',alpha=.35);ax.set_axisbelow(True)
f.text(.10,.055,'The damage study is static (no rerouting after each cut).\nCenters chosen on baseline routes, not sampled from real floods. The geography is approximate.',fontsize=10,color=mut)
f.savefig('out/ten_seed_study.png',bbox_inches='tight',pad_inches=.25)
print('out/ten_seed_study.png')
