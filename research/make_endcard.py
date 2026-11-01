from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
physarum=json.loads(Path('out/benchmark_metrics.json').read_text())['unaffected']['Physarum']['mean_detour_reachable_only']
heuristic=json.loads(Path('out/augmented_mst_metrics.json').read_text())['metrics']['mean_detour_reachable_only']
fig=plt.figure(figsize=(8,10),dpi=135,facecolor='#070a0f')
fig.text(.07,.84,'ONE MORE EXPERIMENT',fontsize=27,fontweight='bold',color='#ffb32c')
fig.text(.07,.75,'Was the slime mold\nactually the best network?',fontsize=26,fontweight='bold',color='#eef2f6',va='top')
fig.text(.07,.54,'MEAN ROUTE DETOUR',fontsize=16,color='#91aabe')
fig.text(.07,.43,f'{physarum:.2f}×',fontsize=60,fontweight='bold',color='#ffb32c')
fig.text(.07,.382,'Physarum-inspired',fontsize=17,color='#eef2f6')
fig.text(.57,.43,f'{heuristic:.2f}×',fontsize=60,fontweight='bold',color='#a5e37b')
fig.text(.57,.382,'Augmented MST',fontsize=17,color='#eef2f6')
fig.text(.07,.27,'THE GRAPH BASELINE WON THIS ROUND.',fontsize=20,fontweight='bold',color='#edf2f6')
fig.text(.07,.195,'Same 16 cities. Same grid. Nearly equal modeled network length.',fontsize=13,color='#b0c0cf')
fig.text(.07,.10,'The interesting part is the trade-off, not a viral claim.',fontsize=13,color='#b0c0cf')
fig.text(.07,.045,'Illustrative geographic model · Seed 7 · Not actual railway tracks',fontsize=10,color='#8ba1b1')
fig.savefig('out/endcard.png',bbox_inches=None,pad_inches=0);plt.close(fig)
