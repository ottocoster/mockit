import requests
import json

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 12345'
}

response = requests.get('https://api.meraki.com/api/v1/organizations', headers=headers, verify=False)
data = response.json()
print(json.dumps(data, indent=4))

if data:
    organization_id = data[0]['id']    
    print(organization_id)
    response = requests.get(f'https://api.meraki.com/api/v1/organizations/{organization_id}/devices?perPage=5000', headers=headers, verify=False)
    print(json.dumps(response.json(), indent=4))



