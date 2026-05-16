import requests
import json

r = requests.get('http://localhost:8000/api/hospitals/')
print("医院列表:")
print(r.text[:2000])
