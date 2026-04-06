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

## Netconf Server

### Info

Netconf mock outputs can be created by editing the `configs/<platform>/netconf/get-config.xml` file. Here's an example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply message-id="{message_id}"
    xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <bgp>
            <bgp-router>
                <router-id>1.1.1.1</router-id>
                <bgp-neighbor>
                    <neighbor-id>2.2.2.2</neighbor-id>
                    <remote-as>65000</remote-as>
                </bgp-neighbor>
                <bgp-neighbor>
                    <neighbor-id>3.3.3.3</neighbor-id>
                    <remote-as>65001</remote-as>
                </bgp-neighbor>
            </bgp-router>
        </bgp>
    </data>
</rpc-reply>
```

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

## Telnet Server

### Info

To enable Telnet server support, set the `TELNET_SERVER_ENABLED` environment variable to `true`. Mock'it supports a wide range of Telnet-enabled devices, including popular vendors like **Cisco**, **Juniper**, **Arista**, and more.

### Supported Telnet Devices
- adtran_os_telnet
- cisco_ios_telnet
- juniper_junos_telnet
For the full list see supported_devices_telnet.md

## Docker Compose Configuration

### Basic Example
The following example demonstrates how to configure the Docker Compose file to simulate a **Cisco IOS** device:

```yaml
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
      - NETCONF_USERNAME=test
      - NETCONF_PASSWORD=test
      - TELNET_USERNAME=test
      - TELNET_PASSWORD=test
      - DEBUG_ENABLED=true
    ports:
      - "22:22"  # SSH
      - "161:161/udp"  # SNMP
      - "23:23"  # Telnet
      - "830:830"  # Netconf
    volumes:
      - ./configs/cisco_ios:/configs/cisco_ios
networks:
  mockit_network:
    driver: bridge
```

### Example with Static IPv4 & IPv6
This example demonstrates how to specify static IP addresses for a mock device:

```yaml
name: devices
services:
  cisco_ios:
    image: registry.gitlab.com/slurpit.io/mockit:latest
    container_name: cisco_ios
    environment:
      - DEVICE_TYPE=cisco_ios
      - SSH_USERNAME=test
      - SSH_PASSWORD=test
      - DEVICE_DELAY=5  # Simulate slow responses
      - LOGIN_DELAY=3
      - LOGIN_RETRY=3
    ports:
      - "22:22"
      - "161:161/udp"
    networks:
      mockit_network:
        ipv4_address: 172.16.240.45
        ipv6_address: fc00::abcd
    volumes:
      - ./configs/cisco_ios:/configs/cisco_ios
networks:
  mockit_network:
    enable_ipv6: true
    driver: bridge
    ipam:
      config:
        - subnet: 172.16.240.0/24
        - subnet: fc00::/64
```

## Environment Variables

### Device Configuration
- **DEVICE_TYPE**: Specifies the type of device to emulate.
- **DEVICE_VERSION**: Use this to simulate different versions of the same device type.

### SSH Configuration
- **SSH_SERVER_ENABLED**: Enable SSH server (default is true).
- **SSH_USERNAME**: SSH username for authentication.
- **SSH_PASSWORD**: SSH password for authentication.
- **SSH_KEX_ALGORITHMS**: Optional comma-separated list of SSH key exchange algorithms to allow (for example `diffie-hellman-group14-sha1`).
- **DEVICE_DELAY**: Introduces a delay before a device responds to a command.
- **LOGIN_DELAY**: Delays the SSH login process.
- **LOGIN_RETRY**: Defines the number of retries for failed login attempts.
- **AUTHKEY_ENABLED**: Enable auth key file authentication of ssh server.
- **AUTHKEY_PATH**: Public keypath of the ssh key

### SNMP Configuration
- **SNMP_V2_ENABLED**: Enable SNMP v2 (default is true).
- **SNMP_V2_COMMUNITY**: SNMP v2 community string (default is "public").
- **SNMP_V3_ENABLED**: Enable SNMP v3 (default is false).
- **SNMP_V3_USERNAME**: Username for SNMP v3.
- **SNMP_V3_AUTH_TYPE**: Authentication type for SNMP v3.
- **SNMP_V3_AUTH_KEY**: Authentication key for SNMP v3.
- **SNMP_V3_PRIV_TYPE**: Privacy type for SNMP v3.
- **SNMP_V3_PRIV_KEY**: Privacy key for SNMP v3.

### Netconf Configuration
- **NETCONF_SERVER_ENABLED**: Enable Netconf server (default is true).
- **NETCONF_USERNAME**: Username for Netconf authentication.
- **NETCONF_PASSWORD**: Password for Netconf authentication.

### Telnet Configuration
- **TELNET_SERVER_ENABLED**: Enable Telnet server (default is true).
- **TELNET_USERNAME**: Telnet username.
- **TELNET_PASSWORD**: Telnet password.

### OpenAI Integration (Optional)
- **OPENAI_SUPPORT**: Enable OpenAI support for handling unknown commands (default is true).
- **OPENAI_APIKEY**: Set your OpenAI API key [here](https://platform.openai.com/).

### Logging Configuration
- **DEBUG_ENABLED**: Enable print debug logs (default is false)

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

# Create the table for VLANs if not exists
create_table('cisco_ios')

def handle_command(command: str):
    if command.startswith("vlan"):
        # Get the VLAN number
        match = re.search(r'vlan (\d+)', command)
        if match:
            vlan_number = match.group(1)
            vlan_name = f"VLAN{vlan_number.zfill(4)}"
            vlan_status = "active"
            vlan_ports = " "  # Default port, you may want to make this configurable

            # Check if VLAN already exists
            existing_vlans = read_record("cisco_ios", "vlan")

            # If VLAN exists, update it; otherwise, create a new record
            if existing_vlans:
                if vlan_name not in existing_vlans:
                    update_record("cisco_ios", "vlan", existing_vlans + f"\n{vlan_number} {vlan_name} {vlan_status} {vlan_ports}")
            else:
                create_record("cisco_ios", "vlan", f"{vlan_number} {vlan_name} {vlan_status} {vlan_ports}")
            return True

    if command == "show vlan brief":
        # Read VLANs from the database
        vlans = read_record("cisco_ios", "vlan")
        if vlans:
            # Format the VLANs into a table
            table_header = "{:<4} {:<32} {:<9} {:<30}".format("VLAN", "Name", "Status", "Ports")
            table_separator = "-" * len(table_header)
            table_rows = [table_header, table_separator]

            # Add each VLAN to the table
            for vlan in vlans.split("\n"):
                vlan_details = vlan.split(" ")
                vlan_row = "{:<4} {:<32} {:<9} {:<30}".format(vlan_details[0], vlan_details[1], vlan_details[2], vlan_details[3])
                table_rows.append(vlan_row)

            # Join the rows into a formatted string
            return "\n".join(table_rows)
```


# Development info

## githook
- `git config core.hooksPath .githooks` to automatically increment the version number

## Contribution

If you want to share your command templates with the rest of us, it would be appreciated.
Simply make a merge request. Make sure the executed command is not in the template, that it's pure output.

# Roadmap
- RestAPI support to imitate controller based devices.