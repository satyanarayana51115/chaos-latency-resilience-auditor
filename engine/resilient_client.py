import time
import httpx

class ResilientInventoryClient:
    def __init__(self, client: httpx.Client, timeout_sec: float = 1.5, max_retries: int = 3):
        self.client = client
        self.timeout_sec = timeout_sec
        self.max_retries = max_retries

    def fetch_with_resilience(self, endpoint: str) -> dict:
        """Executes API calls with strict timeout guardrails and exponential backoff retries."""
        backoff = 0.2
        last_error = ""

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.get(endpoint, timeout=self.timeout_sec)
                
                if response.status_code == 200:
                    data = response.json()
                    data["attempts_taken"] = attempt
                    return data
                
                if response.status_code in (502, 503, 504):
                    last_error = f"HTTP {response.status_code} on attempt {attempt}"
                    if attempt < self.max_retries:
                        time.sleep(backoff)
                        backoff *= 2  # Exponential backoff (0.2s -> 0.4s)
                        continue
                
                response.raise_for_status()

            except httpx.TimeoutException:
                return {
                    "status": "FALLBACK_TRIGGERED",
                    "reason": f"Strict SLA Timeout ({self.timeout_sec}s) breached - prevented thread hang",
                    "attempts_taken": attempt
                }

        return {
            "status": "CIRCUIT_OPEN",
            "reason": f"Exhausted {self.max_retries} retries ({last_error})",
            "attempts_taken": self.max_retries
        }