import requests

resp = requests.get("http://127.0.0.1:8001/openapi.json", timeout=5)
data = resp.json()
paths = [p for p in data["paths"] if "hospital" in p.lower()]
print("医院相关路由:")
for p in paths:
    methods = list(data["paths"][p].keys())
    print(f"  {p}: {methods}")
