import pandas as pd
import numpy as np
import pytest
from sentinel.config import DISTRICTS,SYNDROMES
from sentinel.store import observations,quality,validate,series
from sentinel.signals import detect_signal,district_alerts
from sentinel.prediction import fit_predict,predict
from sentinel.scenarios import simulate
from pipelines.generate_events import generate
from pipelines.stream_etl import transform

def test_dataset_quality():
    stats=quality()
    assert stats['rows']>4000
    assert stats['validation_errors']==[]
    assert stats['missing_combinations']==0
    assert stats['duplicates']==0

def test_schema_validation_rejects_duplicates_and_bad_source():
    df=observations().head(2).copy()
    bad=pd.concat([df,df.iloc[[0]]])
    assert any('Duplicate' in msg for msg in validate(bad))
    df.loc[df.index[0],'source']='ACTUAL'
    assert any('SIMULATED' in msg for msg in validate(df))

def test_signal_does_not_leak_current_window_into_baseline():
    regular=np.full(42,10)
    spike=np.r_[regular, np.full(4,60)]
    result=detect_signal(spike)
    assert result['level']=='high'
    assert result['baseline_cases']==10
    assert detect_signal(np.full(46,10))['level']=='normal'

def test_syndrome_alerts_complete():
    for syndrome in SYNDROMES:
        alerts=district_alerts(syndrome)
        assert len(alerts)==len(DISTRICTS)
        assert {x['district'] for x in alerts}==set(DISTRICTS)

def test_poisson_forecast_not_negative_and_has_backtest():
    y=series('dengue','Dhaka').cases.to_numpy()
    result=fit_predict(y,8)
    assert len(result['forecast'])==8
    assert all(x['cases']>=0 and x['lower']>=0 and x['upper']>=x['cases'] for x in result['forecast'])
    assert result['backtest']['model_mae']>=0
    assert result['backtest']['seasonal_naive_mae']>=0

def test_scenario_zero_reduction_equal_and_more_reduction_saves_more():
    baseline=simulate('ili','Sylhet',0,6)
    active=simulate('ili','Sylhet',40,6)
    assert baseline['difference_total']==0
    assert active['difference_total']>0
    assert active['baseline_total']==baseline['baseline_total']
    assert active['hypothetical_total']<active['baseline_total']

def test_streaming_event_pipeline(tmp_path):
    events=tmp_path/'events.csv';out=tmp_path/'aggregate.csv'
    assert generate(events,1017,71)==1017
    assert transform(events,out,83)==1017
    summary=pd.read_csv(out)
    assert summary.encounters.sum()==1017
    assert summary.cases.le(summary.encounters).all()

@pytest.mark.parametrize('days',[0,13])
def test_reject_invalid_horizon(days):
    with pytest.raises(ValueError):fit_predict(np.ones(100),days)
