import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_pipeline import generate_metrics
from src.model import train_models, score_metrics
from src.triage_agent import triage_incident

st.set_page_config(page_title="OpsPulse | AIOps", page_icon="📡", layout="wide")
st.title("📡 OpsPulse")
st.caption("Infrastructure telemetry · Time-series anomaly detection · Forecasting · Incident triage")

@st.cache_data
def get_data():
    return generate_metrics(1500)

raw = get_data()
if not Path("models/anomaly_detector.joblib").exists():
    with st.spinner("Training demo models..."):
        train_models(raw)
scored = score_metrics(raw)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Telemetry samples", f"{len(scored):,}")
c2.metric("Anomalies detected", int(scored["is_anomaly"].sum()))
c3.metric("Latest CPU", f'{scored.iloc[-1]["cpu_pct"]:.1f}%')
c4.metric("Latest latency", f'{scored.iloc[-1]["latency_ms"]:.0f} ms')

metric = st.selectbox("Metric to inspect", ["cpu_pct", "memory_pct", "latency_ms", "error_rate_pct"])
chart = px.line(scored, x="timestamp", y=metric, title=f"{metric.replace('_', ' ').title()} over time")
anomalies = scored[scored["is_anomaly"]]
if not anomalies.empty:
    chart.add_scatter(x=anomalies["timestamp"], y=anomalies[metric],
                      mode="markers", name="Detected anomaly")
st.plotly_chart(chart, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Next-step latency forecast")
    forecast = px.line(scored.tail(150), x="timestamp",
                       y=["latency_ms", "predicted_latency_next_step"],
                       title="Observed vs predicted latency")
    st.plotly_chart(forecast, use_container_width=True)
with right:
    st.subheader("Detected anomaly samples")
    st.dataframe(anomalies[["timestamp"] + ["cpu_pct", "memory_pct", "latency_ms",
                                           "error_rate_pct", "anomaly_score"]].tail(12),
                 use_container_width=True, hide_index=True)

st.divider()
st.subheader("Incident intelligence")
st.write("Select a detected sample to run the tool-using triage workflow.")
if anomalies.empty:
    st.info("No anomalies detected in this run.")
else:
    choices = anomalies.index.tolist()
    selected = st.selectbox("Anomaly sample", choices, format_func=lambda i: str(scored.loc[i, "timestamp"]))
    report = triage_incident(scored.loc[selected].to_dict())
    st.metric("Suggested severity", report["severity"].upper())
    st.write("**Tools executed:** " + " → ".join(report["tools_executed"]))
    st.write("**Observed metrics**")
    st.json(report["observations"])
    st.write("**Recommended investigation steps**")
    for action in report["recommended_actions"]:
        st.write(f"- {action}")
    st.caption(report["note"])

with st.expander("About this demo and limitations"):
    st.write("The telemetry is synthetic and incidents are injected for demonstration. "
             "The anomaly detector is unsupervised (Isolation Forest). The latency model "
             "predicts one 5-minute step ahead using a chronological holdout. "
             "The triage workflow uses deterministic Python tools, not an LLM or autonomous production agent.")
