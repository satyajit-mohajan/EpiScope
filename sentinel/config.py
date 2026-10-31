from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / 'data' / 'weekly_synthetic.csv'
SYNDROMES = {'dengue': 'Dengue-like syndrome', 'diarrhea': 'Acute diarrheal illness', 'ili': 'Influenza-like illness'}
DISTRICTS = ['Barishal', 'Chattogram', 'Dhaka', 'Khulna', 'Mymensingh', 'Rajshahi', 'Rangpur', 'Sylhet']
# Deliberately simulated population denominators, not actual census figures.
DEMO_POP = {'Barishal': 900000, 'Chattogram': 3100000, 'Dhaka': 5000000,
            'Khulna': 1200000, 'Mymensingh': 1100000, 'Rajshahi': 1300000,
            'Rangpur': 1000000, 'Sylhet': 1200000}
END_DATE = '2026-10-12'
SEED = 9345
