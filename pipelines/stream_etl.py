"""Bounded-memory streamed CSV -> transactional SQLite -> summarized CSV."""
import argparse,csv,sqlite3
from pathlib import Path
from sentinel.config import DISTRICTS,SYNDROMES

def transform(input_csv,output_csv,batch_size=5000):
    if batch_size<1: raise ValueError('batch_size must be positive')
    database=sqlite3.connect(':memory:')
    database.execute('CREATE TABLE encounter (week TEXT,district TEXT,syndrome TEXT,flag INTEGER)')
    count=0;batch=[]
    with open(input_csv,newline='',encoding='utf-8') as fh:
        reader=csv.DictReader(fh)
        if not {'week_start','district','syndrome','case_flag','source'}.issubset(reader.fieldnames or []):
            raise ValueError('Missing encounter CSV header')
        for row in reader:
            flag=int(row['case_flag'])
            if row['source']!='SIMULATED_ENCOUNTER' or row['district'] not in DISTRICTS or row['syndrome'] not in SYNDROMES or flag not in (0,1):
                raise ValueError(f'Invalid synthetic event near row {count+2}')
            batch.append((row['week_start'],row['district'],row['syndrome'],flag))
            if len(batch)>=batch_size:
                database.executemany('INSERT INTO encounter VALUES (?,?,?,?)',batch)
                count+=len(batch);batch=[]
        if batch:
            database.executemany('INSERT INTO encounter VALUES (?,?,?,?)',batch)
            count+=len(batch)
    output_csv=Path(output_csv);output_csv.parent.mkdir(parents=True,exist_ok=True)
    result=database.execute('SELECT week,district,syndrome,COUNT(*),SUM(flag) FROM encounter GROUP BY week,district,syndrome ORDER BY week,district,syndrome')
    with output_csv.open('w',newline='',encoding='utf-8') as fh:
        writer=csv.writer(fh);writer.writerow(['week_start','district','syndrome','encounters','cases'])
        writer.writerows(result)
    database.close()
    return count
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',default='data/encounters_demo.csv')
    p.add_argument('--output',default='data/encounter_aggregates.csv')
    p.add_argument('--batch-size',type=int,default=5000);a=p.parse_args()
    print('Validated, aggregated rows:',transform(a.input,a.output,a.batch_size))
