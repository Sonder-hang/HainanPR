import requests
import json

endpoints = [
    "http://127.0.0.1:8001/api/indicators/hospitals/",
    "http://127.0.0.1:8001/api/system/hospitals/",
    "http://127.0.0.1:8001/api/monitoring/hospitals/",
]

for url in endpoints:
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        print(f"=== {url} ===")
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
        print()
    except Exception as e:
        print(f"=== {url} ===")
        print(f"Error: {e}")
        print()
