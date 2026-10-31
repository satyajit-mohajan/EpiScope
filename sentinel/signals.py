"""Explainable early-warning signals; thresholds illustrative, NOT validated."""
import numpy as np
from .config import DISTRICTS
from .store import series

def detect_signal(values)->dict:
    vals=np.asarray(values,dtype=float)
    if len(vals)<34: raise ValueError('At least 34 weeks of history required')
    baseline=vals[-30:-4]
    latest=vals[-4:]
    baseline_avg=float(np.mean(baseline))
    baseline_sd=float(np.std(baseline,ddof=1))
    z=(float(np.mean(latest))-baseline_avg)/max(baseline_sd/2., np.sqrt(max(1.,baseline_avg))/2.,1.)
    prior=max(1.,float(np.mean(vals[-8:-4])))
    momentum=float(np.mean(latest)/prior)
    if z>=3.0 and momentum>=1.2: level='high'
    elif z>=1.6 and momentum>=1.05: level='watch'
    else: level='normal'
    ewma=float(vals[-30])
    for x in vals[-29:]: ewma=.35*x+.65*ewma
    return {'level':level,'z_score':round(z,2),'four_week_change_pct':round((momentum-1)*100,1),
            'ewma_cases':round(ewma,1),'baseline_cases':round(baseline_avg,1),
            'recent_cases_avg':round(float(np.mean(latest)),1)}

def district_alerts(syndrome):
    result=[]
    for district in DISTRICTS:
        weekly=series(syndrome,district)
        stats=detect_signal(weekly.cases)
        result.append({'district':district,'recent_four_week_cases':int(weekly.cases.iloc[-4:].sum()),
                       'latest_cases':int(weekly.cases.iloc[-1]),**stats})
    priority={'high':0,'watch':1,'normal':2}
    return sorted(result,key=lambda x:(priority[x['level']],-x['z_score']))
