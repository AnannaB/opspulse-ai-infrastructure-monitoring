from pathlib import Path
import numpy as np
import pandas as pd

METRICS = ["cpu_pct", "memory_pct", "latency_ms", "error_rate_pct"]

def generate_metrics(n_rows: int = 1500, seed: int = 42) -> pd.DataFrame:
    """Create reproducible infrastructure telemetry with injected incidents."""
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2026-01-01", periods=n_rows, freq="5min")
    t = np.arange(n_rows)
    daily = np.sin(2 * np.pi * t / 288)
    cpu = 42 + 12 * daily + rng.normal(0, 4, n_rows)
    memory = 52 + 0.006 * t + rng.normal(0, 2.5, n_rows)
    latency = 115 + 22 * daily + rng.normal(0, 12, n_rows)
    errors = np.clip(0.6 + rng.normal(0, 0.18, n_rows), 0, None)

    # Inject several observable incident windows for a useful demo.
    incidents = [(350, 390), (820, 850), (1190, 1225)]
    for start, end in incidents:
        cpu[start:end] += rng.uniform(28, 42)
        memory[start:end] += rng.uniform(15, 25)
        latency[start:end] += rng.uniform(180, 260)
        errors[start:end] += rng.uniform(2.5, 5.0)

    frame = pd.DataFrame({
        "timestamp": timestamps,
        "cpu_pct": np.clip(cpu, 0, 100),
        "memory_pct": np.clip(memory, 0, 100),
        "latency_ms": np.clip(latency, 1, None),
        "error_rate_pct": np.clip(errors, 0, 100),
    })
    return frame

def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Sort, clean and create rolling time-series features."""
    df = frame.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").drop_duplicates("timestamp")
    for col in METRICS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].interpolate(limit_direction="both")
        df[f"{col}_rolling_mean"] = df[col].rolling(6, min_periods=1).mean()
        df[f"{col}_rolling_std"] = df[col].rolling(6, min_periods=1).std().fillna(0)
        df[f"{col}_delta"] = df[col].diff().fillna(0)
    df = df.dropna().reset_index(drop=True)
    return df

def save_dataset(path: str = "data/metrics.csv", n_rows: int = 1500) -> pd.DataFrame:
    raw = generate_metrics(n_rows=n_rows)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(path, index=False)
    return raw
