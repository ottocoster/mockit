#!/usr/bin/env bash
#
# Exercise every API driver against its matching test script.
# Each driver is started on :443, tested, then torn down (only one at a time).
#
# Requirements: docker, and a python with `requests`:
#     python3 -m venv .venv && .venv/bin/pip install requests
#
# Usage:
#     tests/run_api_tests.sh            # auto-detects python+requests
#     PY=.venv/bin/python tests/run_api_tests.sh
#     IMAGE=registry.gitlab.com/slurpit.io/mockit:latest tests/run_api_tests.sh
#
set -u

IMAGE="${IMAGE:-devices-meraki:latest}"
HERE="$(cd "$(dirname "$0")" && pwd)"
export PYTHONWARNINGS=ignore

# --- find a python that has `requests` ---------------------------------------
PY="${PY:-}"
if [ -z "$PY" ]; then
  for c in .venv/bin/python /tmp/apivenv/bin/python python3; do
    if "$c" -c "import requests" 2>/dev/null; then PY="$c"; break; fi
  done
fi
if [ -z "$PY" ] || ! "$PY" -c "import requests" 2>/dev/null; then
  echo "ERROR: need a python with 'requests'."
  echo "  python3 -m venv .venv && .venv/bin/pip install requests"
  echo "  PY=.venv/bin/python tests/run_api_tests.sh"
  exit 1
fi
echo "Using python: $PY    image: $IMAGE"

cleanup() { docker rm -f meraki unifi unifi_cloud greenlake >/dev/null 2>&1 || true; }
trap cleanup EXIT

start_driver() {                 # $1=name, rest=docker -e args
  cleanup
  local name="$1"; shift
  docker run -d --name "$name" -p 443:443 "$@" "$IMAGE" >/dev/null
  for _ in $(seq 1 20); do       # wait until the API answers
    curl -sk -o /dev/null https://localhost:443/ 2>/dev/null && return 0
    sleep 1
  done
  echo "  (warning: $name did not become ready in time)"
}

echo; echo "==================== meraki (Bearer) ===================="
start_driver meraki -e DEVICE_TYPE=meraki -e API_AUTH_TYPE=bearer -e API_TOKEN=12345
MERAKI_BASE=https://localhost MERAKI_TOKEN=12345 "$PY" "$HERE/meraki_api_test.py" | head -20

echo; echo "==================== unifi (X-API-KEY) ===================="
start_driver unifi -e DEVICE_TYPE=unifi -e API_AUTH_TYPE=apikey -e API_KEY=mock-api-key
UNIFI_BASE=https://localhost UNIFI_KEY=mock-api-key "$PY" "$HERE/unifi_api_test.py"

echo; echo "==================== unifi_cloud (X-API-KEY) ===================="
start_driver unifi_cloud -e DEVICE_TYPE=unifi_cloud -e API_AUTH_TYPE=apikey -e API_KEY=mock-api-key
UNIFI_CLOUD_BASE=https://localhost UNIFI_CLOUD_KEY=mock-api-key "$PY" "$HERE/unifi_cloud_test.py"

echo; echo "==================== hpe_greenlake (OAuth2) ===================="
start_driver greenlake -e DEVICE_TYPE=hpe_greenlake -e API_AUTH_TYPE=oauth2 \
  -e API_OAUTH_CLIENT_ID=1234 -e API_OAUTH_CLIENT_SECRET=45678
TOKEN=$(curl -sk -X POST -d "grant_type=client_credentials&client_id=1234&client_secret=45678" \
  https://localhost/authorization/v2/oauth2/56789567456/token \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
echo "issued access_token: $TOKEN"
curl -sk -H "Authorization: Bearer $TOKEN" https://localhost/locations/v1/locations

echo; echo "==================== done ===================="
