# Reproducible methods and limits

**Research question:** Can an explainable, weekly-sentinel demonstrator help students explore signals, forecasting and what-if response assumptions?

**Pipeline:** reproducible NumPy negative-binomial draws -> CSV schema validation -> Pandas weekly sums -> EWMA/anomaly flags + Poisson GLM forecasting -> transparent arithmetic scenario -> FastAPI REST -> HTML/SVG UI. An independent optional encounter streaming ETL shows chunked inserts and SQL aggregation; optional PySpark example writes aggregated Parquet.

**Early warning:** Reference window is weeks [-30:-4], evaluation window [-4:]. Calculate reference mean, reference sample std and mean of latest four weeks. Normalize using the reference standard error with a variance floor, then require a momentum (recent4/prior4) criterion. Watch: z >=1.6 AND ratio >=1.05; high: z >=3.0 AND ratio >=1.20. Otherwise normal. EWMA alpha=.35 is descriptive only.

**Forecast:** count response, Poisson log-link model with two pairs of annual Fourier sin/cos terms and capped time trend; regularization alpha .07. Evaluation holds out the final 12 weeks. Baseline=corresponding count 52 weeks earlier. MAE uses the same holdout. Full history refit only after evaluation. 80% absolute residual quantile gives symmetric historical error display, NOT a formal calibrated uncertainty interval; the model performs worse than seasonal naive for dengue in this build. No tuning performed against the final holdout.

**Scenario:** arithmetic ramp `y_hyp(t)=prediction(t)*(1-R*t/H)`. No intervention efficacy evidence, causal identification, real treatment cost or resource constraint. The chosen percent is a user-defined hypothetical effect.

**Security:** Local prototype has no authentication, rate limits, audit logs, clinical approvals, or real-data compliance. Never deploy on a public server or ingest patient-identifiable information in this state.
