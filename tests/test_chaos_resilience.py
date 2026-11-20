import threading
import time
import httpx
import pytest
import uvicorn
from app.chaos_inventory_api import app
from engine.resilient_client import ResilientInventoryClient

BASE_URL = "http://127.0.0.1:8099"

@pytest.fixture(scope="module", autouse=True)
def live_chaos_server():
    """Starts a real live Uvicorn server in a background thread for true network latency testing."""
    config = uvicorn.Config(app, host="127.0.0.1", port=8099, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(0.5)  # Wait for server startup
    yield
    server.should_exit = True

def test_01_healthy_endpoint_fast_response():
    """Verifies normal sub-second execution when upstream is healthy."""
    with httpx.Client(base_url=BASE_URL) as http:
        resilient = ResilientInventoryClient(http, timeout_sec=1.5)
        result = resilient.fetch_with_resilience("/api/healthy/BN94-18827E")
        assert result["status"] == "AVAILABLE"
        assert result["attempts_taken"] == 1

def test_02_latency_spike_triggers_sla_timeout_fallback():
    """Audits that a 3.0s latency spike is cut off at 1.5s via SLA timeout guardrail."""
    start = time.perf_counter()
    with httpx.Client(base_url=BASE_URL) as http:
        resilient = ResilientInventoryClient(http, timeout_sec=1.5)
        result = resilient.fetch_with_resilience("/api/slow-latency/BN94-18827E")
    elapsed = time.perf_counter() - start

    assert result["status"] == "FALLBACK_TRIGGERED"
    assert elapsed < 2.0  # Proves we did NOT wait the full 3.0s!

def test_03_flaky_503_chaos_self_heals_via_retries():
    """Audits that transient HTTP 503 errors self-heal automatically on the 3rd retry."""
    with httpx.Client(base_url=BASE_URL) as http:
        resilient = ResilientInventoryClient(http, timeout_sec=1.5, max_retries=3)
        result = resilient.fetch_with_resilience("/api/flaky-chaos/BN94-18827E")

    assert result["status"] == "RECOVERED"
    assert result["recovered_on_attempt"] == 3
    assert result["attempts_taken"] == 3