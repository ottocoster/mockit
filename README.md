# Mock'it - The Device Imitator

`Mock'it` is a mockup service that acts as a network device. Currently, it only supports SSH and SNMP. The difference between this project and others is that we reverse-engineered the Netmiko library, allowing every device to respond in a way that makes it compatible with Netmiko, as if it were a real physical network device. As a result, we can currently imitate 115 different network vendors.

## Getting started

1. Store your config files, script logic, or SNMP output for the vendor you want to imitate in the `/config/<device_type>` folder. By default, we have provided a library of examples that you can use out of the box.
2. Modify the compose file to specify the Device OS you would like to imitate.
3. Run: docker compose up -d --build
4. Log in via SSH through the terminal, or run your network automation script against it.

## Device version

It's possible to store different configurations for an OS per version. For example, for Mikrotik, we currently support multiple versions. You can switch between them using DEVICE_VERSION. You can see how it's set up in /config/mikrotik_routeros/.

You can do the same for your own configurations by adding a folder to the `/config/<device_type>/<device_version>` directory and using the folder name as the DEVICE_VERSION.

## SSH Server

### Add a static command

You can add a static command response in `/config/<device_type>/templates`. The name of the file has to equal the command being executed.

### Add a dynamic command

You can create a dynamic command response in `/config/<device_type>/scripts`. Whenever a command is executed, it first goes through the def handle_command function in __init__.py. This allows you to use Python logic to generate your response.
For example:

```python
def handle_command(command: str):
    if command.startswith('show hello'):
         return ("Hello world")
    return ""
```

## SNMP Server

### Info

SNMP examples are currently only provided for a few vendors, as we don't have access to all devices to create an snmp.json. If you have a device from one of the missing vendors, please consider submitting a pull request. To share this information with the project, you can use the following example command:

```bash
snmpwalk -v3 -u usr-md5-des -l authPriv -A authkey1 -X privkey1 localhost .1.3.6
```

## Docker compose

### Example

```yml
name: devices
services:
  cisco_ios:
    image: registry.gitlab.com/slurpit.io/mockit:latest
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

It's possible to map a volume to include your own scripts and templates. By default, the container will use `/config/<device_type>/`. To connect to the device remotely via SSH, port 22 is opened, and for SNMP, port 161/UDP is used.

Environment Options
- DEVICE_TYPE: Supported device types you want to imitate.
- DEVICE_VERSION: Incase your device has different subfolders because of versioning. Look at Mikrotik_routeros as an example.

Environment SSH Options
- SSH_USERNAME: SSH username.
- SSH_PASSWORD: SSH password.
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