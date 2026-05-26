import requests
import json

# 测试执行记录 API
url = 'http://127.0.0.1:8001/api/indicators/execution/'
try:
    resp = requests.get(url, timeout=10)
    data = resp.json()
    print(f'记录数量: {len(data)}')
    if data:
        record = data[0]
        print(f'字段列表: {list(record.keys())}')
        print(f'id: {record.get("id")}')
        print(f'indicator_id: {record.get("indicator_id")}')
        print(f'indicator_name: {record.get("indicator_name")}')
        print(f'status: {record.get("status")}')
        print(f'kind: {record.get("kind")}')
        print(f'execution_time: {record.get("execution_time")}')
except Exception as e:
    print(f'Error: {e}')
