import os
import requests
import json

# Default to the real API; override for mockit:
#   MERAKI_BASE=https://localhost MERAKI_TOKEN=12345 python meraki_api_test.py
BASE = os.environ.get('MERAKI_BASE', 'https://api.meraki.com')
TOKEN = os.environ.get('MERAKI_TOKEN', '12345')

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {TOKEN}'
}

response = requests.get(f'{BASE}/api/v1/organizations', headers=headers, verify=False)
data = response.json()
print(json.dumps(data, indent=4))

if data:
    organization_id = data[0]['id']
    print(organization_id)
    response = requests.get(f'{BASE}/api/v1/organizations/{organization_id}/devices?perPage=5000', headers=headers, verify=False)
    print(json.dumps(response.json(), indent=4))
