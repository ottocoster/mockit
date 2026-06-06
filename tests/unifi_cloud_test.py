import os
import requests
import json

# Default to the real cloud API; override for mockit:
#   UNIFI_CLOUD_BASE=https://localhost UNIFI_CLOUD_KEY=mock-api-key python unifi_cloud_test.py
BASE = os.environ.get('UNIFI_CLOUD_BASE', 'https://api.ui.com')
API_KEY = os.environ.get('UNIFI_CLOUD_KEY', '')

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'X-API-KEY': API_KEY
}

response = requests.get(f'{BASE}/v1/hosts', headers=headers, verify=False)
data = response.json()
print(json.dumps(data, indent=4))
