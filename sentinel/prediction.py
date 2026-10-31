"""Weekly Poisson GLM and chronological holdout (no random-split leakage)."""
from functools import lru_cache
import numpy as np
from sklearn.linear_model import PoissonRegressor
from sklearn.metrics import mean_absolute_error
from .store import series

def features(weeks):
    weeks=np.asarray(weeks,dtype=float)
    theta=2*np.pi*weeks/52.18
    return np.column_stack([np.sin(theta),np.cos(theta),np.sin(2*theta),np.cos(2*theta),
                            np.minimum(weeks/208.,1.6)])

def fit_predict(values,horizon=8):
    y=np.asarray(values,dtype=float)
    if len(y)<80: raise ValueError('Forecast requires at least 80 historical weeks')
    if not 1<=horizon<=12: raise ValueError('Forecast horizon must be 1-12 weeks')
    holdout=12
    cut=len(y)-holdout
    model=PoissonRegressor(alpha=.07,max_iter=400,tol=1e-7)
    model.fit(features(np.arange(cut)),y[:cut])
    test_pred=model.predict(features(np.arange(cut,len(y))))
    actual=y[cut:]
    seasonal_naive=y[np.arange(cut,len(y))-52]
    abs_err=np.abs(test_pred-actual)
    width=float(np.quantile(abs_err,.8))
    model.fit(features(np.arange(len(y))),y)
    projection=np.maximum(0,model.predict(features(np.arange(len(y),len(y)+horizon))))
    return {'forecast':[{'week_offset':i+1,'cases':round(float(v),1),
               'lower':round(max(0.,float(v)-width),1),'upper':round(float(v)+width,1)}
               for i,v in enumerate(projection)],
            'backtest':{'holdout_weeks':holdout,'model_mae':round(float(mean_absolute_error(actual,test_pred)),2),
                'seasonal_naive_mae':round(float(mean_absolute_error(actual,seasonal_naive)),2),
                'empirical_holdout_80_band_coverage':round(float(np.mean(abs_err<=width)),2),
                'residual_band_width':round(width,2)},
            'model':'Poisson GLM / Fourier seasonality + capped trend',
            'note':'Illustrative only; residual bands are not calibrated prediction intervals.'}

@lru_cache(maxsize=128)
def predict(syndrome,district,horizon=8):
    frame=series(syndrome,district)
    result=fit_predict(frame.cases.to_numpy(),horizon)
    end=frame.week_start.iloc[-1]
    import pandas as pd
    for row in result['forecast']:
        row['week_start']=(end+pd.Timedelta(weeks=row['week_offset'])).date().isoformat()
    result['recent']=[{'week_start':r.week_start.date().isoformat(),'cases':int(r.cases)}
                      for r in frame.tail(20).itertuples(index=False)]
    return result
