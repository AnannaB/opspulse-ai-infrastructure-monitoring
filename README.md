# OpsPulse — Infrastructure Anomaly Detection & Incident Intelligence

A compact AIOps portfolio project demonstrating time-series feature engineering, unsupervised anomaly detection, next-step forecasting, a tool-using incident triage workflow, a Streamlit dashboard, Docker packaging and GitHub Actions CI.

## Problem
Infrastructure teams monitor CPU, memory, latency and error-rate metrics. Sudden changes can indicate service degradation. OpsPulse processes telemetry, flags unusual patterns, forecasts latency one sampling interval ahead, and produces investigation suggestions from a small runbook.

## Architecture
1. **Data engineering:** reproducible telemetry generation, timestamp ordering, duplicate removal, missing-value interpolation and rolling-window features.
2. **Time-series ML:** Isolation Forest anomaly detection over current and rolling telemetry features.
3. **Forecasting:** Random Forest regression predicts latency for the next five-minute interval; evaluation uses a chronological holdout and MAE.
4. **Incident intelligence:** a tool-using workflow calls metric inspection and runbook retrieval functions, then assigns a suggested severity.
5. **MLOps / DevOps:** serialized models, repeatable training script, smoke tests, GitHub Actions CI and Docker deployment.

## Quickstart
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python pipeline.py
streamlit run app.py
```
Open the local Streamlit URL printed in the terminal.

## Docker
```bash
docker build -t opspulse .
docker run -p 8501:8501 opspulse
```

## Tests
```bash
pytest -q
```

## Repository structure
```text
opspulse/
├── app.py
├── pipeline.py
├── src/
│   ├── data_pipeline.py
│   ├── model.py
│   └── triage_agent.py
├── tests/
├── models/                 # generated locally; excluded from Git
├── data/                   # generated locally; excluded from Git
├── Dockerfile
├── requirements.txt
└── .github/workflows/ci.yml
```

## Important limitations
- Demo telemetry is synthetic with injected incident windows; it is not production monitoring data.
- Isolation Forest is unsupervised; anomaly flags are not ground-truth incident labels.
- The forecasting model predicts one five-minute step ahead, not long-horizon demand.
- Incident triage is a deterministic tool-using workflow, not an LLM-powered autonomous agent. It offers diagnostic suggestions, not automatic remediation.

## Next improvements
- Ingest Prometheus metrics from a Kubernetes cluster.
- Track experiments and model versions with MLflow.
- Add drift monitoring and scheduled retraining.
- Add an LLM planner with constrained tools and human approval for remediation.
