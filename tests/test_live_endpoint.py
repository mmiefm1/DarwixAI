import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"  # or your ngrok URL, both should behave identically

payload = {
    "message": {
        "toolCallList": [
            {"id": "debug-1", "name": "search_knowledge_base", "arguments": {"query": "What plans do you offer?"}}
        ]
    }
}

resp = requests.post(f"{BACKEND_URL}/voice/search_kb?category=health_insurance", json=payload)
print(f"Status: {resp.status_code}")
print(json.dumps(resp.json(), indent=2))