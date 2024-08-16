# Mock'it - The Device Imitator

`mockit` is a simple ssh server to respond to predefined commands. It was created to be used in integratation tests.

# Development info

## githook
- `git config core.hooksPath .githooks` to automatically increment the version number

## Add new vendor

Create for every new vendor the following folders & snmp file:
- configs/<device_type>/scripts/
- configs/<device_type>/templates/
- configs/<device_type>/snmp.json
- config/<device_type>/<device_type>_server.py

## Test connectivity

Copy or change the docker-compose.dev.yml and replace the following values with the new vendor:
- Services name

Then run /dev/start_dev.sh to spin up your new vendor and use the file ssh_test.py to test and build the connectivity.

## Test connectivity
`ssh -p 22 test@localhost`

## Check Current Port Usage:

`sudo lsof -i -P -n | grep LISTEN | grep :22`

## Stop Conflicting Service:
`sudo systemctl stop ssh`


# Setting up python environment

`export PYTHONPATH=$PYTHONPATH:$(pwd)`
