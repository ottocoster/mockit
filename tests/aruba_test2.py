import requests
import json

BASE_URL = "https://global.api.greenlake.hpe.com"  # or your region
CLIENT_ID = "1234"
CLIENT_SECRET = "45678"

token_url = f"{BASE_URL}/authorization/v2/oauth2/56789567456/token"

payload = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

response = requests.post(token_url, data=payload, headers=headers)
response.raise_for_status()

access_token = response.json()["access_token"]
print("Access token acquired:", access_token)


headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + access_token
}

response = requests.get(f'{BASE_URL}/locations/v1/locations', params={'limit':10}, headers=headers)
data = response.json()
print(json.dumps(data, indent=4))
