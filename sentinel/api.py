"""Local educational demo API - not a production public-health service."""
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from .config import ROOT,DISTRICTS,SYNDROMES,DEMO_POP
from .store import observations,series,quality
from .signals import district_alerts
from .prediction import predict
from .scenarios import simulate

app=FastAPI(title='EpiScope Sentinel - Early Warning Lab',version='2.0',
   description='All source observations synthetic; all outputs educational.')
app.mount('/static',StaticFiles(directory=str(ROOT/'web')),name='static')

def check(syndrome,district='All Districts'):
    if syndrome not in SYNDROMES: raise HTTPException(422,'Invalid syndrome')
    if district!='All Districts' and district not in DISTRICTS: raise HTTPException(422,'Invalid district')

@app.get('/',include_in_schema=False)
def index(): return FileResponse(ROOT/'web'/'index.html')

@app.get('/api/health')
def health(): return {'status':'ok','version':'2.0','simulation_only':True}

@app.get('/api/meta')
def meta(): return {'project':'EpiScope Sentinel','syndromes':SYNDROMES,
 'districts':['All Districts']+DISTRICTS,'demo_population':DEMO_POP,
 'data_label':'SYNTHETIC DEMONSTRATION - NOT REAL PATIENT DATA'}

@app.get('/api/quality')
def data_quality(): return quality()

@app.get('/api/overview')
def overview(syndrome:str='dengue'):
    check(syndrome)
    frame=series(syndrome)
    recent=frame.tail(4);prior=frame.iloc[-8:-4]
    alerts=district_alerts(syndrome)
    return {'syndrome':syndrome,'weeks':len(frame),
      'recent_four_week_cases':int(recent.cases.sum()),
      'prior_four_week_cases':int(prior.cases.sum()),
      'percent_change':round(float((recent.cases.sum()/max(1,int(prior.cases.sum()))-1)*100),1),
      'positivity_pct':round(float(recent.cases.sum()/max(1,int(recent.visits.sum()))*100),1),
      'high_alerts':sum(a['level']=='high' for a in alerts),
      'watch_alerts':sum(a['level']=='watch' for a in alerts),
      'recent_weeks':[{'week_start':r.week_start.date().isoformat(),'cases':int(r.cases),'visits':int(r.visits)}
                       for r in frame.tail(18).itertuples(index=False)],
      'districts':alerts,'simulation_only':True}

@app.get('/api/signals')
def alerts(syndrome:str='dengue'):
    check(syndrome)
    return {'syndrome':syndrome,'alerts':district_alerts(syndrome),
            'disclaimer':'Synthetic unvalidated thresholds; NOT public-health alerts.'}

@app.get('/api/forecast')
def forecast(syndrome:str='dengue',district:str='All Districts',weeks:int=Query(8,ge=1,le=12)):
    check(syndrome,district)
    return {'syndrome':syndrome,'district':district,**predict(syndrome,district,weeks)}

@app.get('/api/scenario')
def scenario(syndrome:str='dengue',district:str='All Districts',
             weeks:int=Query(8,ge=1,le=12),reduction_pct:int=Query(25,ge=0,le=60)):
    check(syndrome,district)
    return simulate(syndrome,district,reduction_pct,weeks)

@app.get('/api/export')
def export(syndrome:str='dengue'):
    check(syndrome)
    frame=observations()
    subset=frame.loc[frame.syndrome==syndrome].copy()
    subset['week_start']=subset.week_start.dt.strftime('%Y-%m-%d')
    return StreamingResponse(iter([subset.to_csv(index=False)]),media_type='text/csv',
     headers={'Content-Disposition':f'attachment; filename="SIMULATED_{syndrome}_weekly.csv"'})
