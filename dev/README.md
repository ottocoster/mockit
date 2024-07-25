# Device Imitator

`device_imitator` is a simple ssh server to respond to predefined commands. It was created to be used in integratation tests.

# Development info

## githook
- `git config core.hooksPath .githooks` to automatically increment the version number

## Add new vendor

Create for every new vendor the following folders & snmp file:
- configs/<device>/scripts/
- configs/<device>/templates/
- configs/<device>/snmp.json

## Test connectivity

Copy or change the docker-compose.dev.yml and replace the following values with the new vendor:
- Services name
- Container name

Then run /dev/start_dev.sh to spin up your new vendor and use the file ssh_test.py to test and build the connectivity.

## Test connectivity