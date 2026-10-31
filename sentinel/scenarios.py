"""Transparent NON-CAUSAL 'what-if' arithmetic over forecasts."""
from .prediction import predict

def simulate(syndrome,district,reduction_pct=25,weeks=8):
    if not 0<=reduction_pct<=60: raise ValueError('Reduction must be 0-60%')
    if not 1<=weeks<=12: raise ValueError('Weeks must be 1-12')
    baseline=predict(syndrome,district,weeks)['forecast']
    rows=[]
    for i,item in enumerate(baseline):
        effect=reduction_pct/100*((i+1)/weeks)
        mitigated=item['cases']*(1-effect)
        rows.append({'week_start':item['week_start'],'baseline':item['cases'],
                     'hypothetical':round(mitigated,1),'difference':round(item['cases']-mitigated,1)})
    return {'syndrome':syndrome,'district':district,'reduction_pct':reduction_pct,'weeks':weeks,
            'baseline_total':round(sum(x['baseline'] for x in rows),1),
            'hypothetical_total':round(sum(x['hypothetical'] for x in rows),1),
            'difference_total':round(sum(x['difference'] for x in rows),1),
            'series':rows,
            'interpretation':'Arithmetic counterfactual; no evidence that reductions are achievable or causal.',
            'planning_ideas':{'dengue':['Source reduction visits','Vector surveillance','Rapid diagnostics'],
                              'diarrhea':['Water-quality sampling','Safe-water messaging','Oral rehydration supplies'],
                              'ili':['Respiratory hygiene messaging','Sentinel testing','Clinic surge preparation']}[syndrome]}
