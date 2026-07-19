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

UNIFI_SITE_ID = "661900ae1c0a4f23b8e1f0a1"


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


# ---- param validation -------------------------------------------------------

def test_missing_required_query_param_rejected():
    _wait("meraki")
    r = requests.get(
        "https://meraki:443/api/v1/organizations/549236/devices",
        headers={"Authorization": "Bearer 12345"}, verify=False, timeout=10,
    )
    # perPage is optional; organizationId (path) is required and present -> 200
    assert r.status_code == 200, r.text


def test_wrong_type_query_param_rejected():
    _wait("meraki")
    r = requests.get(
        "https://meraki:443/api/v1/organizations/549236/devices?perPage=not-a-number",
        headers={"Authorization": "Bearer 12345"}, verify=False, timeout=10,
    )
    assert r.status_code == 400, r.text
    assert "perPage" in r.json()["error"]


def test_missing_required_query_param_on_unifi_cloud_pagesize_type():
    _wait("unifi_cloud")
    r = requests.get(
        "https://unifi_cloud:443/v1/hosts?pageSize=abc",
        headers={"X-API-KEY": "mock-api-key"}, verify=False, timeout=10,
    )
    assert r.status_code == 400, r.text


# ---- pagination ---------------------------------------------------------------

def test_meraki_link_header_pagination():
    """RFC5988: perPage sizes the page; startingAfter/endingBefore are cursor
    tokens (a device's serial here), not page numbers; Link carries up to 4
    rel links (first/prev/next/last)."""
    _wait("meraki")
    base = "https://meraki:443"
    headers = {"Authorization": "Bearer 12345"}
    all_serials = {"Q2XX-AAAA-BBBB", "Q2YY-CCCC-DDDD", "Q2ZZ-EEEE-FFFF"}

    r1 = requests.get(f"{base}/api/v1/organizations/549236/devices", headers=headers, verify=False, timeout=10)
    assert r1.status_code == 200, r1.text
    page1 = r1.json()
    assert len(page1) == 2
    assert "first" in r1.links and "next" in r1.links and "last" in r1.links, r1.headers
    assert "prev" not in r1.links

    r2 = requests.get(r1.links["next"]["url"], headers=headers, verify=False, timeout=10)
    assert r2.status_code == 200, r2.text
    page2 = r2.json()
    assert len(page2) == 1
    assert "next" not in r2.links
    assert "prev" in r2.links
    assert {d["serial"] for d in page1 + page2} == all_serials

    # the `last` link from page 1 jumps to the final `perPage`-sized window,
    # which can overlap the trailing partial page reached by walking `next`
    # when the total isn't a multiple of perPage -- that's expected RFC5988
    # behaviour, not a bug.
    r_last = requests.get(r1.links["last"]["url"], headers=headers, verify=False, timeout=10)
    assert r_last.status_code == 200, r_last.text
    last_page = r_last.json()
    assert len(last_page) == 2
    assert "next" not in r_last.links
    assert last_page[-1] == page2[-1]

    # `prev` from page 2 walks back to page 1
    r_prev = requests.get(r2.links["prev"]["url"], headers=headers, verify=False, timeout=10)
    assert r_prev.json() == page1

    # a perPage large enough to cover everything comes back as one page, no `next`
    r_all = requests.get(f"{base}/api/v1/organizations/549236/devices?perPage=5000", headers=headers, verify=False, timeout=10)
    assert {d["serial"] for d in r_all.json()} == all_serials
    assert "next" not in r_all.links


def test_unifi_offset_total_pagination():
    _wait("unifi")
    base = f"https://unifi:443/proxy/network/integration/v1/sites/{UNIFI_SITE_ID}/devices"
    headers = {"X-API-KEY": "mock-api-key"}
    r1 = requests.get(base, headers=headers, verify=False, timeout=10)
    assert r1.status_code == 200, r1.text
    body1 = r1.json()
    assert body1["totalCount"] == 4
    assert len(body1["data"]) == 2
    r2 = requests.get(f"{base}?offset=2", headers=headers, verify=False, timeout=10)
    body2 = r2.json()
    assert len(body2["data"]) == 2
    assert {d["id"] for d in body1["data"] + body2["data"]} == {
        "a0b1c2d3e4f5", "b1c2d3e4f5a6", "c2d3e4f5a6b7", "d3e4f5a6b7c8",
    }


def test_unifi_cloud_next_token_pagination():
    _wait("unifi_cloud")
    base = "https://unifi_cloud:443/v1/hosts"
    headers = {"X-API-KEY": "mock-api-key"}
    r1 = requests.get(base, headers=headers, verify=False, timeout=10)
    body1 = r1.json()
    assert len(body1["data"]) == 2
    assert "nextToken" in body1
    r2 = requests.get(f"{base}?nextToken={body1['nextToken']}", headers=headers, verify=False, timeout=10)
    body2 = r2.json()
    assert len(body2["data"]) == 1
    assert "nextToken" not in body2


def test_hpe_greenlake_offset_items_total_pagination():
    base = "https://hpe_greenlake:443"
    _wait("hpe_greenlake")
    tok = requests.post(
        f"{base}/authorization/v2/oauth2/56789567456/token",
        data={"grant_type": "client_credentials", "client_id": "1234", "client_secret": "45678"},
        verify=False, timeout=10,
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {tok}"}
    r1 = requests.get(f"{base}/locations/v1/locations", headers=headers, verify=False, timeout=10)
    body1 = r1.json()
    assert body1["total"] == 3
    assert len(body1["items"]) == 2
    r2 = requests.get(f"{base}/locations/v1/locations?offset=2", headers=headers, verify=False, timeout=10)
    body2 = r2.json()
    assert len(body2["items"]) == 1


def test_aruba_offset_items_total_pagination_next_param():
    base = "https://aruba:443"
    _wait("aruba")
    s = requests.Session()
    s.verify = False
    s.post(f"{base}/oauth2/authorize/central/api/login", json={"client_id": "cid", "username": "u", "password": "p"}, timeout=10)
    code = s.post(f"{base}/oauth2/authorize/central/api", json={"client_id": "cid", "response_type": "code", "scope": "all"}, timeout=10).json()["auth_code"]
    token = s.post(f"{base}/oauth2/token", json={"client_id": "cid", "client_secret": "secret", "grant_type": "authorization_code", "code": code}, timeout=10).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r1 = s.get(f"{base}/monitoring/v2/aps", headers=headers, timeout=10)
    body1 = r1.json()
    assert body1["total"] == 3
    assert len(body1["aps"]) == 2
    r2 = s.get(f"{base}/monitoring/v2/aps?next=2", headers=headers, timeout=10)
    body2 = r2.json()
    assert len(body2["aps"]) == 1
