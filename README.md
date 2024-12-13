# Mock'it - The Device Imitator

`Mock'it` is a mockup service that acts as a network device. Currently, it only supports SSH and SNMP. The difference between this project and others is that we reverse-engineered the Netmiko library, allowing every device to respond in a way that makes it compatible with Netmiko, as if it were a real physical network device. As a result, we can currently imitate 115 different network vendors.

## Getting started

1. Store your config files, script logic, or SNMP output for the vendor you want to imitate in the `/config/<device_type>` folder. By default, we have provided a library of examples that you can use out of the box.
2. Modify the compose file to specify the Device OS you would like to imitate.
3. Run: docker compose up -d --build
4. Log in via SSH through the terminal, or run your network automation script against it.

## YouTube playlist with sample videos

https://www.youtube.com/playlist?list=PLxv8A8sCq4EBPfeJGk_Ufb5l9NT50qil2

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
# Linux (sudo apt install snmp)
snmpwalk -v2c -c public localhost

# Windows (http://www.snmpsoft.com)
snmpwalk -v:"2" -c:"public" -r:"localhost"
```
## NETCONF Support

### Test the connectivity

```bash
# Connect to the netconf server
ssh test@localhost -p 830 -s netconf

# Using netconf-console 
netconf-console2 --host localhost --port 830 -u test -p test
```

### Get the running configuration with ncclient

```python
from ncclient import manager

# Connect to the device
with manager.connect(
    host='localhost',
    port=830,
    username='test',
    password='test',
    hostkey_verify=False
) as m:
    
    # Get the running configuration
    running_config = m.get_config('running')
    print(running_config)
```

## Docker compose

### Basic example

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
      - NETCONF_USERNAME=test
      - NETCONF_PASSWORD=test
      - DEVICE_DELAY=5
      - LOGIN_DELAY=3
      - LOGIN_RETRY=3
    ports: 
      - "22:22"
      - "161:161/udp"
      - "830:8830"
    volumes:
      - ./configs/cisco_ios:/configs/cisco_ios

networks:
  devices-network:
    driver: bridge
```

### Example with static IPv4 & IPv6
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
      - DEVICE_DELAY=5 # Simulate slow responses
      - LOGIN_DELAY=3 # Simulate slow login
      - LOGIN_RETRY=3 # Simulate automatic login failures
    ports: 
      - "22:22"
      - "161:161/udp"
    networks:
      devices-network:
        ipv4_address: 172.16.240.45 # change to what ipv4 you prefer
        ipv6_address: fc00::abcd # change to what ipv6 you prefer
    volumes:
      - ./configs/cisco_ios:/configs/cisco_ios

networks:
  devices-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.16.240.0/24
        - subnet: fc00::/64
```

### Info

It's possible to map a volume to include your own scripts and templates. By default, the container will use `/config/<device_type>/`. To connect to the device remotely via SSH, port 22 is opened, and for SNMP, port 161/UDP is used.

Environment Options
- DEVICE_TYPE: Supported device types you want to imitate.
- DEVICE_VERSION: Incase your device has different subfolders because of versioning. Look at Mikrotik_routeros as an example.

Environment SSH Options
- SSH_USERNAME: SSH username.
- SSH_PASSWORD: SSH password.
- NETCONF_USERNAME: NETCONF username.
- NETCONF_PASSWORD: NETCONF password.
- DEVICE_DELAY: Adds a delay (in seconds) before responding to a command.
- LOGIN_DELAY: Adds a delay (in seconds) before the server accepts an SSH connection.
- LOGIN_RETRY: Defines the number of retries allowed for login attempts.

Environment SNMP Options
- SNMP_V2_ENABLED: Enable SNMP V2 (default true)
- SNMP_V2_COMMUNITY: SNMP community string (default public)
- SNMP_V3_ENABLED: Enable SNMP V2 (default false)
- SNMP_V3_USERNAME: SNMPv3 Username
- SNMP_V3_AUTH_TYPE: SNMPv3 Authentication Type
- SNMP_V3_AUTH_KEY: SNMPv3 Authentication Key
- SNMP_V3_PRIV_TYPE: SNMPv3 Privilege Type
- SNMP_V3_PRIV_KEY: SNMPv3 Privilege Key

OpenAI
- OPENAI_SUPPORT: Have OpenAI to respond to unknown cli commands (default true)
- OPENAI_APIKEY: Get your api key at https://platform.openai.com/ 

## Device Configuration

We created a module where you can use a simple database manager to Create, Read, Update and Delete data.
This way you can create your own configuration logic, see the following YouTube video for more details
https://www.youtube.com/watch?v=fMtLNYJ3708&list=PLxv8A8sCq4EBPfeJGk_Ufb5l9NT50qil2

### Database Options:
- create_table
- create_record
- read_record
- update_record
- delete_record

### Example

configs\cisco_ios\scripts\__init__.py
```python
from src.ssh_server.db_operations import create_table, create_record, read_record, update_record, delete_record
import re
create_table('cisco_ios')
def handle_command(command: str):
    if command.startswith("add vlan"):

        # Get the vlan number
        match = re.search(r'add vlan (\d+)', command)
        if match:
            vlan_number = match.group(1)

            db_vlan = read_record("cisco_ios","vlan")
            if db_vlan:
                update_record("cisco_ios", "vlan", db_vlan + " " + vlan_number)
            else:
                create_record("cisco_ios", "vlan", vlan_number)
            
            # Return the device prompt
            return True

    if command == "show vlans":
        vlans = read_record("cisco_ios", "vlan")
        if vlans:
            return vlans
        else:
            return True
    return ""
```


# Development info

## githook
- `git config core.hooksPath .githooks` to automatically increment the version number

## Contribution

If you want to share your command templates with the rest of us, it would be appreciated.
Simply make a merge request. Make sure the executed command is not in the template, that it's pure output.

# Roadmap
- Telnet support
- RestAPI support to imitate controller based devices.