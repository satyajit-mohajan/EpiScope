"""Schema validation and deterministic aggregation, with no network IO."""
from functools import lru_cache
import pandas as pd
from .config import DATA_CSV, DISTRICTS, SYNDROMES
REQUIRED = ['week_start','district','syndrome','cases','visits','source']

def validate(frame: pd.DataFrame) -> list[str]:
    issues=[]
    missing=set(REQUIRED).difference(frame.columns)
    if missing: return [f'Missing fields: {sorted(missing)}']
    if frame.empty: return ['Dataset is empty']
    dates=pd.to_datetime(frame['week_start'], errors='coerce')
    if dates.isna().any(): issues.append('Invalid week_start dates')
    if not frame['district'].isin(DISTRICTS).all(): issues.append('Unknown districts')
    if not frame['syndrome'].isin(SYNDROMES).all(): issues.append('Unknown syndromes')
    if not frame['source'].eq('SIMULATED_SENTINEL').all(): issues.append('Source must equal SIMULATED_SENTINEL')
    for field in ['cases','visits']:
        val=pd.to_numeric(frame[field],errors='coerce')
        if val.isna().any() or (val<0).any() or ((val%1)!=0).any():
            issues.append(f'{field} must be nonnegative integers')
    try:
        numeric=frame[['cases','visits']].apply(pd.to_numeric)
        if (numeric.cases>numeric.visits).any(): issues.append('cases cannot exceed visits')
    except Exception: pass
    if frame.duplicated(['week_start','district','syndrome']).any():
        issues.append('Duplicate week/district/syndrome keys')
    if not dates.isna().any() and (dates.dt.weekday!=0).any():
        issues.append('week_start must be Mondays')
    return issues

@lru_cache(maxsize=1)
def observations():
    if not DATA_CSV.exists():
        from .generator import generate
        generate()
    frame=pd.read_csv(DATA_CSV)
    problems=validate(frame)
    if problems: raise ValueError('Invalid demo data: '+'; '.join(problems))
    frame['week_start']=pd.to_datetime(frame['week_start'])
    return frame

def series(syndrome: str, district: str='All Districts') -> pd.DataFrame:
    data=observations()
    subset=data[data.syndrome==syndrome]
    if district!='All Districts': subset=subset[subset.district==district]
    return subset.groupby('week_start',as_index=False)[['cases','visits']].sum().sort_values('week_start')

def quality():
    frame=observations()
    weeks=frame.week_start.nunique()
    return {'rows':len(frame),'districts':len(DISTRICTS),'syndromes':len(SYNDROMES),
            'weeks':weeks,'expected_rows':weeks*len(DISTRICTS)*len(SYNDROMES),
            'missing_combinations':weeks*len(DISTRICTS)*len(SYNDROMES)-len(frame),
            'duplicates':int(frame.duplicated(['week_start','district','syndrome']).sum()),
            'date_min':frame.week_start.min().date().isoformat(),
            'date_max':frame.week_start.max().date().isoformat(),
            'validation_errors':validate(frame),'synthetic':True}
