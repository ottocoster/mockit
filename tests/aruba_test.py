import requests
import json
import time
import keyring

from requests.auth import HTTPBasicAuth, AuthBase
from authlib.integrations.requests_client import OAuth2Session
from authlib.integrations.base_client.errors import OAuthError

def refresh_access_token(client_id, client_secret, refresh_token):
    response = requests.post(
        "https://api-ap.central.arubanetworks.com/oauth2/token",
        json={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )
    return response.json()  # contains new access_token + refresh_token

def request_access_token2(client_id, client_secret):
    response = requests.post(
        "https://apigw-eucentral2.central.arubanetworks.com/oauth2/token",
        json={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
    )
    return response.json()  # contains new access_token + refresh_token

def request_authorization_code(client_id):
    response = requests.post(
        "https://apigw-eucentral2.central.arubanetworks.com/oauth2/authorize/central/api/login",
        json={
            "client_id": client_id
        }
    )
    return response.json()


def request_access_token(client_id, client_secret, customer_id):
    with requests.Session() as session:
        response = session.post(
            "https://api-ap.central.arubanetworks.com/oauth2/authorize/central/api/login",
            json={
                "client_id": client_id,
                "username": "@gmail.com",
                "password": "$"
            }
        )
        print(response.json())
        response.raise_for_status()
        response = session.post(
            "https://api-ap.central.arubanetworks.com/oauth2/authorize/central/api",
            json={
                "client_id": client_id,
                "customer_id": customer_id,
                "response_type": "code",
                "scope": "all"
            }
        )
        data = response.json()
        print(data)
        response.raise_for_status()
        auth_code = data['auth_code']
        response = session.post(
            "https://api-ap.central.arubanetworks.com/oauth2/token",
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "code": auth_code
            }
        )
        return response.json()

def validate_token(tokens):
        if not tokens["expires_at"]:
            return False
        return time.time() < (tokens["expires_at"] - 60)

def load_tokens(client_id, client_secret, customer_id):
    tokens = keyring.get_password("slurpit.retriever", client_id)
    if tokens:
        tokens = json.loads(tokens)
        if validate_token(tokens):
            return tokens
    tokens = request_access_token(client_id, client_secret, customer_id)
    if "expires_in" in tokens:
        tokens["expires_at"] = time.time() + int(tokens["expires_in"])
    keyring.set_password("slurpit.retriever", client_id, json.dumps(tokens))
    return tokens

tokens = load_tokens("","", "")

print(tokens)

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + tokens['access_token']
}

response = requests.get('https://api-ap.central.arubanetworks.com/monitoring/v2/aps', headers=headers)
data = response.json()
print(json.dumps(data, indent=4))

# if data:
#     organization_id = data[0]['id']    
#     print(organization_id)
#     response = requests.get(f'https://api.meraki.com/api/v1/organizations/{organization_id}/devices?perPage=5000', headers=headers, verify=False)
#     print(json.dumps(response.json(), indent=4))



