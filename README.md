# Mock'it - The Device Imitator

`Mock'it` is a mockup service which acts as a Network Device. Currently it only supports SSH & SNMP.
Difference with this project compared to other projects is that we reversed engineered the Netmiko library, so that every device will respond in such a way that you can talk to it with Netmiko like it's a real physical network device. For this reason we can currently imitate 115 different network vendors.

## Getting started

1. Store you config files, script logic or SNMP output for the vendor you want to imitate in the /config/<device> folder.
   By default we already provided a library of examples which you can use out of the box.
2. Change the compose file to which Device OS you would like to imitate
3. Run: docker compose up -d --build
4. Login with SSH via the terminal, or run your network automatisch script against it.

## Device version

It's possible to store different configurations for a OS per version. For example, For mikrotik we currently support multiple versions. With `DEVICE_VERSION` you can switch between the two. You can see how it's setup in /config/mikrotik_routeros/.

You can do the same for your own folder to the config/<device> folder just use the folder name as the `DEVICE_VERSION`.

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

SNMP examples are currently only provided for a couple vendors since we don't have all the devices to provide a snmp.json, but if you do have 1 of the missing vendors please submit a pull request. To share this information with the project you can use the following example command:

```bash
snmpwalk -v3 -u usr-md5-des -l authPriv -A authkey1 -X privkey1 localhost .1.3.6
```

## Docker compose

### Example

```yml
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
- DEVICE_TYPE: Supported device types you want to imitate.

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


# Roadmap

- AI integration to reply on missing commands
- Simple ORM to store networking information if you want to build for example a vlan.dat
- NetConf support
- RestAPI support to imitate controller based devices.