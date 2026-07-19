"""
Simulates the exact payload Vapi sends when a tool call fires, so you can
verify /voice/search_kb works correctly BEFORE touching the Vapi dashboard.

Usage:
    python test_voice_endpoint.py "What is the loan due date policy?"
"""
import sys
import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"  # match your running backend port

def test_voice_endpoint(query: str):
    # This mimics Vapi's real webhook payload shape exactly
    fake_vapi_payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {
                    "id": "test-call-id-123",
                    "name": "search_knowledge_base",
                    "arguments": {"query": query}
                }
            ]
        }
    }

    print(f"Sending query: {query!r}\n")
    resp = requests.post(f"{BACKEND_URL}/voice/search_kb", json=fake_vapi_payload)

    print(f"Status code: {resp.status_code}")
    print("Response body:")
    print(json.dumps(resp.json(), indent=2))

    # Sanity checks matching what Vapi requires
    body = resp.json()
    assert resp.status_code == 200, "Vapi requires HTTP 200 always -- this would fail silently in production"
    assert "results" in body, "Response must have a top-level 'results' key"
    assert body["results"][0]["toolCallId"] == "test-call-id-123", "toolCallId must be echoed back exactly"
    assert isinstance(body["results"][0]["result"], str), "result must be a plain string"
    assert "\n" not in body["results"][0]["result"], "result must be single-line (no newlines)"

    print("\n✅ All checks passed -- this endpoint is ready for Vapi.")


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "What is the loan pre-due reminder policy?"
    test_voice_endpoint(query)