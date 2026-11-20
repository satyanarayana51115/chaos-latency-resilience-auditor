import time
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Chaos & Latency Inventory API", version="1.0")

# Tracks attempt counts per part_id to simulate transient 503 recovery
attempt_tracker: dict[str, int] = {}

@app.get("/api/healthy/{part_id}")
def get_healthy_part(part_id: str):
    """Normal fast-responding endpoint."""
    return {"part_code": part_id, "status": "AVAILABLE", "source": "PRIMARY_DB"}

@app.get("/api/slow-latency/{part_id}")
def get_slow_part(part_id: str):
    """Simulates a severe 3-second downstream database latency spike."""
    time.sleep(3.0)
    return {"part_code": part_id, "status": "AVAILABLE", "source": "SLOW_REPLICA"}

@app.get("/api/flaky-chaos/{part_id}")
def get_flaky_part(part_id: str):
    """Simulates transient 503 failures on first 2 calls, succeeding on the 3rd attempt."""
    current_attempt = attempt_tracker.get(part_id, 0) + 1
    attempt_tracker[part_id] = current_attempt

    if current_attempt < 3:
        raise HTTPException(
            status_code=503,
            detail=f"Chaos Fault Injected: Upstream node overloaded (Attempt {current_attempt}/3)"
        )
    
    return {
        "part_code": part_id,
        "status": "RECOVERED",
        "recovered_on_attempt": current_attempt
    }