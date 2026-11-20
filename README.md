# ⚡ Chaos & Latency Resilience Auditor (SDET Series: Project 3/3)

An automated Resilience & Fault-Injection Testing framework built with **Python, FastAPI, Uvicorn, HTTPX, and Pytest** to audit microservice stability against severe network latency spikes and transient `HTTP 503` outages.

## 🎯 Problem Statement

In distributed architectures, downstream services frequently suffer from sudden latency spikes (hanging threads) or intermittent `502/503/504` service errors. Without strict client-side guardrails, a single slow upstream endpoint can trigger cascading failures across the entire platform.

## ⚙️ Architecture & Resilience Guardrails

* **Chaos & Latency Injector API (`app/chaos_inventory_api.py`):** Simulates healthy sub-second responses (`/api/healthy/{id}`), severe `3.0s` database latency spikes (`/api/slow-latency/{id}`), and transient `503 Service Unavailable` outages (`/api/flaky-chaos/{id}`).

* **Resilient Client Engine (`engine/resilient_client.py`):** Enforces a strict `1.5s` SLA timeout guardrail (triggering immediate fallback before thread starvation) and automated **Exponential Backoff Retries** (`0.2s -> 0.4s`) for transient `5xx` faults.

* **Live Network Chaos Audit (`tests/test_chaos_resilience.py`):** Spins up a live background Uvicorn server to validate real TCP timeout cutoffs and self-healing recovery across 3 scenarios.


## 📁 Project Structure

```text
chaos-latency-resilience-auditor/
├── app/
│   └── chaos_inventory_api.py      # FastAPI server with latency & 503 fault injection
├── engine/
│   └── resilient_client.py         # SLA Timeout & Exponential Backoff retry client
├── tests/
│   └── test_chaos_resilience.py    # Live Uvicorn + Pytest chaos audit suite
├── reports/
│   └── chaos_resilience_report.html # Self-contained HTML resilience report
├── assets/                         # Execution proof screenshots
├── pytest.ini
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

```
# Install dependencies
pip install -r requirements.txt

# Run Chaos & Latency Resilience Audit
pytest -v -rA --html=reports/chaos_resilience_report.html --self-contained-html

```

## 📊 Execution Proof

​test_01_healthy_endpoint_fast_response: PASSED (Sub-second response on attempt 1)
​test_02_latency_spike_triggers_sla_timeout_fallback: PASSED (Cut off a 3.0s hang at 1.5s via SLA fallback guardrail)
​test_03_flaky_503_chaos_self_heals_via_retries: PASSED (Self-healed transient HTTP 503 failures on attempt 3 via exponential backoff)

​1. Terminal Chaos Audit Results

​2. Pytest HTML Resilience Report