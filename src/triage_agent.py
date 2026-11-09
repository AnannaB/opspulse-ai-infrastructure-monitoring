from typing import Callable

def inspect_metrics(row: dict) -> dict:
    """Tool: summarize the latest telemetry sample."""
    return {
        "cpu_pct": round(float(row["cpu_pct"]), 1),
        "memory_pct": round(float(row["memory_pct"]), 1),
        "latency_ms": round(float(row["latency_ms"]), 1),
        "error_rate_pct": round(float(row["error_rate_pct"]), 2),
    }

def retrieve_runbook(metrics: dict) -> list[str]:
    """Tool: retrieve concise runbook actions from metric conditions."""
    actions = []
    if metrics["cpu_pct"] >= 85:
        actions.append("Check recent deployments and identify CPU-heavy processes; inspect pod CPU throttling.")
    if metrics["memory_pct"] >= 85:
        actions.append("Check memory growth, restart history and container memory limits; inspect for leaks.")
    if metrics["latency_ms"] >= 250:
        actions.append("Inspect upstream dependency latency, request queues and database connection pools.")
    if metrics["error_rate_pct"] >= 2:
        actions.append("Group errors by endpoint and correlate with the latest deployment or dependency failures.")
    if not actions:
        actions.append("No threshold-specific runbook matched. Compare recent telemetry with the baseline.")
    return actions

def triage_incident(row: dict) -> dict:
    """Small tool-using workflow: inspect -> select runbook -> produce recommendation."""
    metrics = inspect_metrics(row)
    runbook = retrieve_runbook(metrics)
    severity = "high" if (
        metrics["latency_ms"] >= 300 or metrics["error_rate_pct"] >= 4
        or metrics["cpu_pct"] >= 95 or metrics["memory_pct"] >= 95
    ) else "medium" if len(runbook) > 1 else "low"
    return {
        "severity": severity,
        "observations": metrics,
        "tools_executed": ["inspect_metrics", "retrieve_runbook"],
        "recommended_actions": runbook,
        "note": "Recommendations are diagnostic suggestions; validate before taking production action."
    }
