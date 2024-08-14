# Device Imitator

`device_imitator` is a simple ssh server to respond to predefined commands. It was created to be used in integratation tests.

## Work in progress

There are still a lot of basic commands, more functionality and more devices to add

## Getting started

The previously retrieved command output needs to be stored in a directory, one per device. The file needs to be named as the exact command.

## Device version

For mikrotik we currently support multiple version. With `DEVICE_VERSION` you can switch between the two. We will probably add more version for devices in the future.

You can add your own folder to the config/<device> folder for your own version and use the folders name as the `DEVICE_VERSION`

## SSH Server

### Add a static command

You can add a static command response in `/config/<device>/templates`. The name of the file has to equal the command being executed

### Add a dynamic command

You can create a dynamic command response in `/config/<device>/scripts`. Whenever a command is called, it first goes thought the `def handle_command` in __init__.py. This way you can use python logic to build your return response.
For example:

```python
def handle_command(command: str):
    if command.startswith('show hello'):
         return ("Hello world")
    return ""
```

## SNMP Server

### Info

SNMP currently only works for a couple vendors. 
We don't have all the devices to provide a snmp.json, but if you do have 1 of the missing vendors please submit a pull request.

## Docker compose

### Example

```yml
version: "3"
name: devices
services:
  cisco_ios:
    image: registry.gitlab.com/slurpit.io/device_imitator:latest
    container_name: cisco_ios
    environment:
      - DEVICE_TYPE=cisco_ios
      - SSH_USERNAME=test
      - SSH_PASSWORD=test
      - DEVICE_DELAY=5
      - LOGIN_DELAY=3
      - LOGIN_RETRY=3
    ports: 
      - "22:22"
      - "161:161/udp"
    volumes:
      - ./configs/cisco_ios:/configs/cisco_ios
```

### Info

It's optional to map a volume, by default we will go for /config/<device>/
To connect to the device remotely through ssh we open the 22 port and for snmp the 161/udp port.

Environment Options
- DEVICE_TYPE: Supported device type you want to imitate.

Environment SSH Options
- SSH_USERNAME: SSH username.
- SSH_PASSWORD: SSH password.
- DEVICE_VERSION: Incase your device has different subfolders because of versioning. Look at Mikrotik_routeros as an example.
- DEVICE_DELAY: Adds a delay (in seconds) before responding to a command.
- LOGIN_DELAY: Adds a delay (in seconds) before the server accepts an SSH connection.
- LOGIN_RETRY: Defines the number of retries allowed for login attempts.

Environment SNMP Options
- SNMP_V2_ENABLED: Enable SNMP V2 (default enabled)
- SNMP_V2_COMMUNITY: SNMP community string (default public)
- SNMP_V3_ENABLED: Enable SNMP V2 (default disabled)
- SNMP_V3_USERNAME: SNMPv3 Username
- SNMP_V3_AUTH_TYPE: SNMPv3 Authentication Type
- SNMP_V3_AUTH_KEY: SNMPv3 Authentication Key
- SNMP_V3_PRIV_TYPE: SNMPv3 Privilege Type
- SNMP_V3_PRIV_KEY: SNMPv3 Privilege Key

# Development info

## githook
- `git config core.hooksPath .githooks` to automatically increment the version number

## Contribution

If you want to share your command templates with the rest of us, it would be appreciated.
Simply make a merge request. Make sure the executed command is not in the template, that it's pure output.


