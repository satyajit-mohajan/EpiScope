# EpiScope Sentinel - Early Warning & Intervention Scenario Lab

**Independent academic prototype** for *CSE 4345: Complex Engineering Assignment*, Department of Computer Science & Engineering, Premier University, Chattogram.

> **SIMULATED DATA ONLY.** Every included record, cluster, date-series, population denominator, alert classification and reduction scenario is fabricated or hypothetical. NOT for clinical diagnosis, outbreak response, or resource deployment. No actual patient identifiers exist in the included dataset.

## Why this variant is distinct
This project is an independent interpretation of EpiScope focused on **weekly syndromic signals and transparent scenario exploration**. It has its own `sentinel/` architecture, top-navigation light-theme UI, yearly Fourier **Poisson count regression**, **EWMA/standardized anomaly and momentum** early-warning engine, a **ramp-based non-causal what-if simulator**, and **streaming event aggregation** scripts. It is not simply the first project's color-swapped code, day-level Ridge prediction or budget optimizer.

## Features
| Screen | Function |
|---|---|
| Pulse | Latest four-week simulated case burden, visit ratio, week trend and area status |
| Signals | Area-level standardized anomaly score, momentum, EWMA and illustrative flags |
| Forecast | Next 1-12 weeks using seasonal Poisson GLM; 12-week chronological holdout, 52-week seasonal naive comparator and approximate residual bands |
| Scenarios | Hypothetical 0-60% gradually increasing effect over 1-12 weeks; arithmetic baseline and assumed trajectory |
| Data Lab | Schema validation, duplicates, dates, CSV export and API documentation |

## Quick Start (Windows, Python 3.10+)
**Option A**: Double-click `START_WINDOWS.bat`. The script creates `.venv`, installs requirements and starts the app.

**Option B** (PowerShell in the project folder):
```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn sentinel.api:app --host 127.0.0.1 --port 8000
```
Open **http://127.0.0.1:8000** for the dashboard or **http://127.0.0.1:8000/docs** for API docs. Stop with Ctrl+C. The app runs locally; internet is required only for initial package installation.

Linux/macOS: `bash START_MAC_LINUX.sh`. Docker: `docker build -t episcope-sentinel . && docker run --rm -p 8000:8000 episcope-sentinel`.

## Repo structure
```
EpiScope_Sentinel_Friend/
  sentinel/      # FastAPI, validation, Poisson model, alerts, scenarios
  web/           # Interactive vanilla HTML/CSS/JS dashboard (no CDN)
  data/          # Reproducible 4,752-row synthetic weekly CSV
  pipelines/     # Synthetic event stream, SQLite aggregation, optional Spark
  tests/         # 12 unit and integration tests
  assets/        # Captured UI screenshots
  docs/          # Data dictionary, method details, editable report generator
  presentation/  # Editable ten-slide presentation
  START_WINDOWS.bat
  requirements.txt
```

## Data and scale
- 198 **weekly** observations from 2023-01-02 through 2026-10-12.
- 8 labeled Bangladesh district areas and 3 disease-like syndrome streams.
- Exactly 198 x 8 x 3 = **4,752 synthetic aggregate rows**, plus optional generated event samples.
- `source` is always `SIMULATED_SENTINEL`, and synthetic outbreaks are injected by predetermined rules.
- The included data are **not 'Big Data' by volume**. A separate **streaming/chunk-loading pipeline** and optional PySpark exercise demonstrate scalable design patterns. Neither is an operational distributed cluster.

Reproduce weekly CSV:
```bash
python -m sentinel.generator
```
Generate **120,000 additional fake event rows** (no names or patient identifiers), and aggregate them in bounded batches:
```bash
python -m pipelines.generate_events --rows 120000
python -m pipelines.stream_etl --batch-size 5000
```
The fake event stream is a **separate engineering exercise**, not a source that can be mixed with the weekly data. Generated event/output files are Git-ignored. Optional distributed ETL requires manually installing/configuring PySpark and Java, then `python -m pipelines.spark_optional`.

## Models and responsible interpretation
**Signals**: four-week recent average against the immediately preceding 26 weeks. Anomaly `z = (mean_recent4 - mean_prior26) / max(sd_prior26 / sqrt(4), sqrt(mean_prior26) / sqrt(4), 1)`. High if z >= 3 and growth >= 20%; watch if z >= 1.6 and growth >= 5%; otherwise normal. EWMA smoothing uses alpha=0.35 and is shown independently. These are **arbitrary classroom threshold examples**, not validated alerts.

**Forecast**: `PoissonRegressor` of weekly case totals on two annual Fourier harmonics and a capped time trend. Last 12 weeks are withheld before model selection/evaluation. Compare out-of-time mean absolute error (MAE) against previous-year (52-week-lag) naive projection. Train final model on full data for 1-12 week outlook. Plot +/- 80th percentile absolute holdout residual; this **must not be interpreted as a calibrated predictive interval**. The model does not win on every syndrome; see results.

**Scenarios**: for a user selected eventual reduction `r`, at future week `t` of horizon `H`, assume `hypothetical_t = forecast_t * (1-r*t/H)`. The cumulative difference is arithmetic **not a causal intervention estimate**.

## API
`/api/health`, `/api/meta`, `/api/quality`, `/api/overview?syndrome=dengue`, `/api/signals?syndrome=ili`, `/api/forecast?syndrome=dengue&district=Dhaka&weeks=8`, `/api/scenario?syndrome=dengue&district=Dhaka&weeks=8&reduction_pct=25`, `/api/export?syndrome=dengue`.

## Tests
```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```
**Observed verification in this build: 12 passed.** Frontend API loading was also checked with scripted, mocked-browser rendering; backend endpoints were tested with FastAPI TestClient.

## Submission / authorship
The cover pages intentionally contain `[FRIEND GROUP NAME]`, `[MEMBER / STUDENT ID]`, `[FRIEND GITHUB REPO URL]` and a **blank Video Presentation URL** until the group supplies their information. Do not submit with placeholders. Put this project in the **friend's separate repo**, edit report/slide cover accordingly, and record a truthful demonstration/video that the group can explain.

- `EpiScope_Sentinel_Friend_Report.pdf` - new 10-page report (also in root ZIP).
- `presentation/EpiScope_Sentinel_Friend_Presentation.pptx` - new editable 10-slide presentation.
- `docs/make_report.py` can regenerate the report for supplied cover metadata.

This is a **research/engineering demo, not a production public-health tool**. Protect any future real patient data using authorized sources, ethics approvals, consent/legal basis, encryption, access control and professional validation before any deployment.
