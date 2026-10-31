# Test evidence and interpretation

Verified command: `python -m pytest -q`

Result at artifact generation: **12 passed**, Python test environment with FastAPI TestClient, pandas, scikit-learn.

Verified properties: synthetic dataset row count/completeness; schema violation detection; synthetic pulse signal trigger; district signal coverage; nonnegative Poisson forecasts and holdout; zero vs higher scenario comparison; 1,017-event streaming aggregation consistency; invalid horizons and query rejection; static frontend response; API outputs, CSV download.

Repeat tests in a clean Python environment after extraction. No evidence of real-world epidemic accuracy or scalability claims is provided by these tests.
