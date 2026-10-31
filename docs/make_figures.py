"""Publication-style figures from synthetic data and measured model output."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sentinel.config import SYNDROMES
from sentinel.store import series
from sentinel.signals import district_alerts
from sentinel.prediction import predict
from sentinel.scenarios import simulate
OUT=ROOT/'assets';OUT.mkdir(exist_ok=True)
VIOLET='#6259d6';TEAL='#14a9a3';GREY='#9ea8be';INK='#15264a'

def setup(ax):
    ax.set_facecolor('white')
    for spine in ['top','right','left']:ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#e5eaf4')
    ax.grid(axis='y',color='#e9edf5',lw=.9)
    ax.tick_params(axis='both',colors='#72829c',length=0,labelsize=9)
    ax.set_axisbelow(True)

fig,ax=plt.subplots(figsize=(10,4),dpi=160)
for disease,color in [('dengue',VIOLET),('diarrhea',TEAL),('ili','#e9a16e')]:
    frame=series(disease).tail(75)
    ax.plot(frame.week_start,frame.cases,label=SYNDROMES[disease],color=color,lw=2.2)
setup(ax);ax.legend(frameon=False,ncol=3,loc='upper left',fontsize=9)
ax.set_ylabel('Synthetic weekly cases',color=INK)
fig.tight_layout();fig.savefig(OUT/'disease_trends.png',bbox_inches='tight',facecolor='white');plt.close(fig)

p=predict('ili','All Districts',8)
fig,ax=plt.subplots(figsize=(10,4),dpi=160)
obs=p['recent'];f=p['forecast'];n=len(obs)
ax.plot(range(n),[x['cases'] for x in obs],color=VIOLET,lw=2.6,label='Simulated past')
ax.plot(range(n-1,n+8),[obs[-1]['cases']]+[x['cases'] for x in f],color=TEAL,lw=2.5,linestyle='--',label='Poisson projection')
ax.fill_between(range(n,n+8),[x['lower'] for x in f],[x['upper'] for x in f],color=TEAL,alpha=.18,label='Approx. residual band')
setup(ax);ax.legend(frameon=False,loc='upper left',fontsize=9)
ax.set_xlabel('Consecutive weeks (last 20 observed + 8 projected)');ax.set_ylabel('Simulated weekly cases')
fig.tight_layout();fig.savefig(OUT/'forecast_figure.png',bbox_inches='tight',facecolor='white');plt.close(fig)

vals=simulate('dengue','All Districts',30,8)['series']
fig,ax=plt.subplots(figsize=(10,4),dpi=160)
xs=np.arange(len(vals)); ax.bar(xs-.18,[v['baseline'] for v in vals],width=.35,color=VIOLET,label='Forecast baseline')
ax.bar(xs+.18,[v['hypothetical'] for v in vals],width=.35,color=TEAL,label='Hypothetical trajectory')
setup(ax);ax.set_xticks(xs,[f'W{i+1}' for i in range(8)]);ax.legend(frameon=False,loc='upper left',fontsize=9)
ax.set_ylabel('Simulated cases');fig.tight_layout();fig.savefig(OUT/'scenario_figure.png',bbox_inches='tight',facecolor='white');plt.close(fig)

alerts=district_alerts('ili')
fig,ax=plt.subplots(figsize=(9,4.4),dpi=160)
rows=sorted(alerts,key=lambda x:x['z_score']);y=np.arange(len(rows))
colors=['#e9a16e' if r['level']=='watch' else '#8293c7' for r in rows]
ax.barh(y,[r['z_score'] for r in rows],color=colors,height=.65)
ax.set_yticks(y,[r['district'] for r in rows]);ax.axvline(1.6,ls='--',color='#e9a16e',lw=1.5,label='Watch score threshold')
setup(ax);ax.legend(frameon=False,loc='lower right',fontsize=9);ax.set_xlabel('Illustrative standardized anomaly score')
fig.tight_layout();fig.savefig(OUT/'alert_figure.png',bbox_inches='tight',facecolor='white');plt.close(fig)
print('Generated assets')
