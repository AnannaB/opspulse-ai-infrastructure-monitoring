from src.data_pipeline import generate_metrics, add_features
from src.model import train_models
from src.triage_agent import triage_incident

def test_feature_pipeline():
    df = add_features(generate_metrics(100))
    assert len(df) == 100
    assert "cpu_pct_rolling_mean" in df.columns

def test_triage_tools():
    result = triage_incident({
        "cpu_pct": 96, "memory_pct": 90, "latency_ms": 350, "error_rate_pct": 5
    })
    assert result["severity"] == "high"
    assert "retrieve_runbook" in result["tools_executed"]

def test_training_smoke(tmp_path):
    result = train_models(generate_metrics(180), model_dir=str(tmp_path))
    assert result["mae"] >= 0
