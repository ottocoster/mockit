import os
import requests
import json

# Default to the real controller; override for mockit:
#   UNIFI_BASE=https://localhost UNIFI_KEY=mock-api-key python unifi_api_test.py
BASE = os.environ.get('UNIFI_BASE', 'https://192.168.68.52')
API_KEY = os.environ.get('UNIFI_KEY', '')

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'X-API-KEY': API_KEY
}

response = requests.get(f'{BASE}/proxy/network/integration/v1/sites', headers=headers, verify=False)
data = response.json().get('data', [])
print(json.dumps(data, indent=4))
