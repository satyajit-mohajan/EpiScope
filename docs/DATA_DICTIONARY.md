# Simulated weekly surveillance data dictionary

| Column | Type | Meaning | Validation |
|---|---|---|---|
| `week_start` | ISO YYYY-MM-DD | Monday of simulated week | Parseable Monday date |
| `district` | Category | One of eight demonstration Bangladesh district labels | Controlled list |
| `syndrome` | Category | dengue, diarrhea, ili | Controlled list |
| `cases` | Integer | Fabricated syndrome-like case reports during week | 0 <= cases <= visits |
| `visits` | Integer | Fabricated sentinel visits during week | Nonnegative integer |
| `source` | Constant | `SIMULATED_SENTINEL` | All rows must have this label |

Composite key: `(week_start, district, syndrome)`. Data span 2023-01-02 to 2026-10-12, 198 weeks, three streams, eight locations, exactly 4,752 records. Group area labels are geographic names only; **counts are not real surveillance**.

Optional `pipelines/generate_events.py` writes separate simulated `week_start,district,syndrome,case_flag,source` records (`source=SIMULATED_ENCOUNTER`) for a bounded-memory stream-aggregation exercise. These two demos are independent and should not be merged as if they represent one population.
