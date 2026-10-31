"""Generate a configurable stream of fabricated encounter-like rows (NOT individuals)."""
import argparse,csv,random
from pathlib import Path
from sentinel.config import DISTRICTS,SYNDROMES

def generate(path,rows=120000,seed=712):
    randomizer=random.Random(seed)
    with open(path,'w',newline='',encoding='utf-8') as output:
        writer=csv.writer(output)
        writer.writerow(['week_start','district','syndrome','case_flag','source'])
        # Avoid identifiers, patient details, timestamps or any personal data.
        for i in range(rows):
            week=1+i%52
            from datetime import date,timedelta
            dt=date(2025,1,6)+timedelta(weeks=week-1)
            writer.writerow([dt.isoformat(),randomizer.choice(DISTRICTS),
                             randomizer.choice(list(SYNDROMES)),int(randomizer.random()<.3),'SIMULATED_ENCOUNTER'])
    return rows
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rows',type=int,default=120000)
    p.add_argument('--output',default='data/encounters_demo.csv');a=p.parse_args()
    if not 1<=a.rows<=1000000: p.error('--rows must be 1..1000000')
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    print('Wrote synthetic rows:',generate(a.output,a.rows))
