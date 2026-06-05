import requests
import json

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'X-API-KEY': ''
}

response = requests.get('https://192.168.68.52/proxy/network/integration/v1/sites', headers=headers, verify=False)
data = response.json().get('data', [])
print(json.dumps(data, indent=4))
# if data:
#     siteId = data[0]['id']    
#     response = requests.get(f'https://192.168.68.52/proxy/network/integration/v1/sites/{siteId}/devices?pageSize=5000', headers=headers, verify=False)
#     print(json.dumps(response.json(), indent=4))



