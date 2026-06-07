"""
API-driver tests. Each driver runs as its own service on the test network
reachable at https://<service>:443.
"""
import time

import pytest
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# driver service name -> auth header, a GET path, and a validator on the body
SIMPLE_DRIVERS = {
    "meraki": {
        "headers": {"Authorization": "Bearer 12345"},
        "path": "/api/v1/organizations",
        "check": lambda d: d[0]["id"] == "549236",
    },
    "unifi": {
        "headers": {"X-API-KEY": "mock-api-key"},
        "path": "/proxy/network/integration/v1/sites",
        "check": lambda d: d["data"][0]["name"] == "Default",
    },
    "unifi_cloud": {
        "headers": {"X-API-KEY": "mock-api-key"},
        "path": "/v1/hosts",
        "check": lambda d: len(d["data"]) >= 1,
    },
}


def _wait(host, timeout=90):
    """Block until the driver's HTTPS port answers (any status counts)."""
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            requests.get(f"https://{host}:443/", verify=False, timeout=3)
            return
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1)
    raise RuntimeError(f"{host} not reachable: {last}")


@pytest.mark.parametrize("host", list(SIMPLE_DRIVERS))
def test_authorized(host):
    cfg = SIMPLE_DRIVERS[host]
    _wait(host)
    r = requests.get(f"https://{host}:443{cfg['path']}", headers=cfg["headers"], verify=False, timeout=10)
    assert r.status_code == 200, r.text
    assert cfg["check"](r.json()), r.text


@pytest.mark.parametrize("host", list(SIMPLE_DRIVERS))
def test_unauthorized(host):
    cfg = SIMPLE_DRIVERS[host]
    _wait(host)
    r = requests.get(f"https://{host}:443{cfg['path']}", verify=False, timeout=10)
    assert r.status_code == 401, r.text


def test_greenlake_oauth2_client_credentials():
    base = "https://hpe_greenlake:443"
    _wait("hpe_greenlake")
    tok = f"{base}/authorization/v2/oauth2/56789567456/token"
    bad = requests.post(tok, data={"grant_type": "client_credentials", "client_id": "1234", "client_secret": "WRONG"}, verify=False, timeout=10)
    assert bad.status_code == 401, bad.text
    ok = requests.post(tok, data={"grant_type": "client_credentials", "client_id": "1234", "client_secret": "45678"}, verify=False, timeout=10)
    assert ok.status_code == 200, ok.text
    token = ok.json()["access_token"]
    res = requests.get(f"{base}/locations/v1/locations", headers={"Authorization": f"Bearer {token}"}, verify=False, timeout=10)
    assert res.status_code == 200, res.text
    assert res.json()["items"][0]["name"] == "Amsterdam Datacenter"
    assert requests.get(f"{base}/locations/v1/locations", verify=False, timeout=10).status_code == 401


def test_aruba_oauth2_authorization_code():
    base = "https://aruba:443"
    _wait("aruba")
    s = requests.Session()
    s.verify = False
    assert s.post(f"{base}/oauth2/authorize/central/api/login", json={"client_id": "cid", "username": "u", "password": "p"}, timeout=10).status_code == 200
    authz = s.post(f"{base}/oauth2/authorize/central/api", json={"client_id": "cid", "response_type": "code", "scope": "all"}, timeout=10)
    assert authz.status_code == 200, authz.text
    code = authz.json()["auth_code"]
    tok = s.post(f"{base}/oauth2/token", json={"client_id": "cid", "client_secret": "secret", "grant_type": "authorization_code", "code": code}, timeout=10)
    assert tok.status_code == 200, tok.text
    token = tok.json()["access_token"]
    aps = s.get(f"{base}/monitoring/v2/aps", headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert aps.status_code == 200, aps.text
    assert aps.json()["aps"][0]["name"] == "mock-ap-01"
    bad = s.post(f"{base}/oauth2/token", json={"client_id": "cid", "client_secret": "secret", "grant_type": "authorization_code", "code": "WRONG"}, timeout=10)
    assert bad.status_code == 401, bad.text
    assert s.get(f"{base}/monitoring/v2/aps", timeout=10).status_code == 401
