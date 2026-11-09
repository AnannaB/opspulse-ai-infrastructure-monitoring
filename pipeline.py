import json
from pathlib import Path
from src.data_pipeline import save_dataset
from src.model import train_models

def main():
    raw = save_dataset()
    result = train_models(raw)
    scored = result["data"]
    Path("data").mkdir(exist_ok=True)
    scored.to_csv("data/scored_metrics.csv", index=False)
    report = {
        "rows_processed": int(len(scored)),
        "anomalies_detected": int(scored["is_anomaly"].sum()),
        "latency_forecast_mae_ms": round(result["mae"], 2),
        "features": 16
    }
    Path("models/training_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
