"""Generate weekly, district-level, SIMULATED syndrome surveillance counts."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from .config import DATA_CSV, DISTRICTS, SYNDROMES, END_DATE, SEED


def generate(destination: Path = DATA_CSV, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range('2023-01-02', END_DATE, freq='W-MON')
    rows = []
    multipliers = {'Dhaka': 1.9, 'Chattogram': 1.45, 'Rajshahi': .96,
                   'Khulna': 1.11, 'Sylhet': 1.06, 'Barishal': .82,
                   'Rangpur': .89, 'Mymensingh': 1.01}
    for district in DISTRICTS:
        for syndrome in SYNDROMES:
            previous = 0.0
            for i, dt in enumerate(dates):
                phase = (dt.dayofyear - 1) / 365.25 * (2 * np.pi)
                if syndrome == 'dengue':
                    seasonal = max(0., np.sin(phase - 1.70))
                    mean = 15 + 85 * seasonal ** 2
                elif syndrome == 'diarrhea':
                    seasonal = .5 + .5 * np.sin(phase - .35)
                    mean = 29 + 38 * seasonal
                else:
                    seasonal = .5 + .5 * np.cos(phase - .15)
                    mean = 18 + 64 * seasonal
                # Deliberate SIMULATED clusters, NOT historical outbreaks.
                if district == 'Dhaka' and syndrome == 'dengue' and 115 <= i <= 121:
                    mean *= 1.85
                if district == 'Sylhet' and syndrome == 'ili' and 178 <= i <= 183:
                    mean *= 1.7
                if district == 'Khulna' and syndrome == 'diarrhea' and 187 <= i <= 192:
                    mean *= 1.6
                expected = max(1, multipliers[district] * mean + .17 * previous)
                cases = int(rng.negative_binomial(14, 14 / (14 + expected)))
                visits = cases + int(rng.poisson(max(15, cases * 1.85)))
                previous = float(cases)
                rows.append((dt.date().isoformat(), district, syndrome, cases, visits, 'SIMULATED_SENTINEL'))
    result = pd.DataFrame(rows, columns=['week_start','district','syndrome','cases','visits','source'])
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(destination, index=False)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(DATA_CSV))
    args = parser.parse_args()
    out = generate(Path(args.output))
    print(f'Generated {len(out):,} explicitly simulated weekly records -> {args.output}')
