import os
import requests
import json

# Default to the real Mist cloud; override for mockit:
#   MIST_BASE=https://localhost MIST_TOKEN="Token mock-api-token" python juniper_mist_api_test.py
BASE = os.environ.get('MIST_BASE', 'https://api.mist.com')
TOKEN = os.environ.get('MIST_TOKEN', '')

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': TOKEN
}

site_id = '5e5a1e40-0000-4000-8000-000000000001'
response = requests.get(f'{BASE}/api/v1/sites/{site_id}/devices?limit=2', headers=headers, verify=False)
print(json.dumps(response.json(), indent=4))
print('X-Page-Total:', response.headers.get('X-Page-Total'))
