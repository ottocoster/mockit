import requests
import json

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'X-API-KEY': ''
}

response = requests.get('https://api.ui.com/v1/hosts', headers=headers)
data = response.json()
print(json.dumps(data, indent=4))

# print("----------------")
# hostId = data['data'][1]['hostId']

# params={
#     "pageSize": 1
# }
# response = requests.get(f'https://api.ui.com/v1/devices?hostIds[]={hostId}&pageSize=1', headers=headers)
# data = response.json()
# print(json.dumps(data, indent=4))


