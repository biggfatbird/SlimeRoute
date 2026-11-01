import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=json.load(open('out/threshold_sensitivity.json'))['damage_radius_study_same_25_fixed_centers']
x=[v['radius_km'] for v in r]; y=[v['fraction_fully_connected']*100 for v in r]
plt.rcParams.update({'figure.facecolor':'#070a0f','savefig.facecolor':'#070a0f','axes.facecolor':'#101b27','axes.labelcolor':'#f0f4f8','xtick.color':'#9cb4c7','ytick.color':'#9cb4c7','text.color':'#f0f4f8'})
fig,ax=plt.subplots(figsize=(10,6),dpi=160);fig.subplots_adjust(top=.72,bottom=.20,left=.12,right=.94)
fig.text(.10,.94,'HOW BIG A DISRUPTION CAN IT HANDLE?',fontsize=20,weight='bold')
fig.text(.10,.87,'Static Physarum network, seed 7 · Same 25 preselected damage sites',fontsize=11,color='#9cb4c7')
ax.plot(x,y,'o-',color='#ffb32c',markersize=10,lw=3)
for xx,yy in zip(x,y): ax.text(xx,yy+5,f'{yy:.0f}%',ha='center',fontsize=12,color='#eaf0f6')
ax.set_ylim(0,112);ax.set_xlim(55,270);ax.set_xticks(x)
ax.set_xlabel('Blocked disk radius (model km)',fontsize=12,labelpad=9)
ax.set_ylabel('Sites retaining all 120 city connections (%)',fontsize=12,labelpad=9)
ax.grid(alpha=.25,color='#657487');ax.set_axisbelow(True)
fig.text(.10,.075,'No rerouting is permitted in this particular analysis. This is not a real-flood prediction.',fontsize=10,color='#9cb4c7')
fig.savefig('out/damage_radius_sensitivity.png',bbox_inches='tight',pad_inches=.2)
