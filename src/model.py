from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from .data_pipeline import METRICS, add_features

FEATURES = METRICS + [f"{m}_{suffix}" for m in METRICS for suffix in
                      ("rolling_mean", "rolling_std", "delta")]

def train_models(raw: pd.DataFrame, model_dir: str = "models") -> dict:
    """Train unsupervised anomaly detector and next-step latency regressor."""
    df = add_features(raw)
    X = df[FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0)
    detector = IsolationForest(n_estimators=150, contamination=0.035, random_state=42)
    detector.fit(X)
    df["anomaly_score"] = -detector.decision_function(X)
    df["is_anomaly"] = detector.predict(X) == -1

    # Predict latency five minutes ahead using current telemetry features.
    X_forecast = X.iloc[:-1]
    y_forecast = df["latency_ms"].shift(-1).dropna()
    X_train, X_test, y_train, y_test = train_test_split(
        X_forecast, y_forecast, test_size=0.2, shuffle=False
    )
    forecaster = RandomForestRegressor(n_estimators=120, max_depth=8, random_state=42, n_jobs=-1)
    forecaster.fit(X_train, y_train)
    predictions = forecaster.predict(X_test)
    mae = float(mean_absolute_error(y_test, predictions))

    Path(model_dir).mkdir(parents=True, exist_ok=True)
    joblib.dump(detector, Path(model_dir) / "anomaly_detector.joblib")
    joblib.dump(forecaster, Path(model_dir) / "latency_forecaster.joblib")
    joblib.dump(FEATURES, Path(model_dir) / "features.joblib")
    return {"data": df, "mae": mae, "detector": detector, "forecaster": forecaster}

def score_metrics(raw: pd.DataFrame, model_dir: str = "models") -> pd.DataFrame:
    df = add_features(raw)
    detector = joblib.load(Path(model_dir) / "anomaly_detector.joblib")
    forecaster = joblib.load(Path(model_dir) / "latency_forecaster.joblib")
    X = df[FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["anomaly_score"] = -detector.decision_function(X)
    df["is_anomaly"] = detector.predict(X) == -1
    df["predicted_latency_next_step"] = forecaster.predict(X)
    return df
