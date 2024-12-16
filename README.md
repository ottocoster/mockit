# Mock'it - The Device Imitator

Mock'it is an advanced mockup service designed to simulate network devices for use in automation and testing environments. It supports a variety of protocols such as SSH, SNMP, Netconf, and Telnet. Through reverse-engineering of the **Netmiko** library, Mock'it allows devices to respond in a manner consistent with real network devices, making it an invaluable tool for simulating network devices from over 115 vendors.

## Key Features:
- **Device Compatibility**: Imitates 115+ network vendors with support for SSH, SNMP, Netconf, and Telnet.
- **Customizable Command Responses**: Supports both static and dynamic responses, with Python-based logic for generating custom responses.
- **Version Support**: Handle multiple device versions through version-specific configurations.
- **Docker-Based Setup**: Easy deployment with Docker Compose for a flexible, containerized mock network environment.
- **Integrations**: Optionally integrate with OpenAI for handling unknown CLI commands.

## Getting Started

### 1. Store Device Configurations
Place your configuration files, script logic, or SNMP output for the vendor you wish to imitate in the `/config/<device_type>` folder. Mock'it comes with preconfigured examples to help you get started quickly.

### 2. Modify the Compose File
Customize the `docker-compose.yml` file to specify the device OS and any other environment variables you need.

### 3. Build and Run the Mock Device
Run the following Docker Compose command to build and start the mock devices:

```bash
docker compose up -d --build
```

### 4. Access the Device
- Log in via **SSH** through the terminal.
- Alternatively, you can access the device by using netmiko sdk.

## Supported Protocols

### SSH Server
Mock'it supports SSH connections to simulate real device behavior. You can:
- Add **static command responses** by placing templates in `/config/<device_type>/templates` (file names should match the command).
- Create **dynamic command responses** with Python logic in `/config/<device_type>/scripts`. Example:

```python
def handle_command(command: str):
    if command.startswith('show hello'):
        return "Hello world"
    return ""
```

### SNMP Server
Mock'it supports SNMP simulations for a range of device vendors, with more being added over time. If you have a device from a vendor not yet supported, consider contributing a **pull request**.

- To capture SNMP data, you can use the following command:
  
  ```bash
  # Linux (sudo apt install snmp)
  snmpwalk -v2c -c public localhost
  ```

  Or, for Windows:

  ```bash
  # Windows (http://www.snmpsoft.com)
  snmpwalk -v:"2" -c:"public" -r:"localhost"
  ```

### Netconf Server
Custom Netconf servers can be created with tailored command responses by editing `src/start_netconf.py`. Here's an example for handling a basic Netconf request:

```python
nc_server.expect_request(
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<nc:rpc xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="{message_id}">'
    "<nc:get-config><nc:source><nc:running/></nc:source></nc:get-config>"
    "</nc:rpc>"
).respond_with("""
    <?xml version="1.0" encoding="UTF-8"?>
    <rpc-reply message-id="{message_id}"
        xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <data>OK</data>
    </rpc-reply>
""")
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

### Telnet Server
To enable Telnet server support, set the `TELNET_SERVER_ENABLED` environment variable to `true`. Mock'it supports a wide range of Telnet-enabled devices, including popular vendors like **Cisco**, **Juniper**, **Arista**, and more.

### Supported Telnet Devices
- adtran_os_telnet
- cisco_ios_telnet
- juniper_junos_telnet
- and many more.

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
      - NETCONF_SERVER_ENABLED=true
      - NETCONF_USERNAME=test
      - NETCONF_PASSWORD=test
      - TELNET_SERVER_ENABLED=true
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
  devices-network:
    driver: bridge
```

### Example with Static IPv4 & IPv6
This example demonstrates how to specify static IP addresses for the mock device:

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
      devices-network:
        ipv4_address: 172.16.240.45
        ipv6_address: fc00::abcd
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

## Environment Variables

### Device Configuration
- **DEVICE_TYPE**: Specifies the type of device to emulate.
- **DEVICE_VERSION**: Use this to simulate different versions of the same device type.

### SSH Configuration
- **SSH_USERNAME**: SSH username for authentication.
- **SSH_PASSWORD**: SSH password for authentication.
- **DEVICE_DELAY**: Introduces a delay before a device responds to a command.
- **LOGIN_DELAY**: Delays the SSH login process.
- **LOGIN_RETRY**: Defines the number of retries for failed login attempts.

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
- **NETCONF_SERVER_ENABLED**: Enable Netconf server (default is false).
- **NETCONF_USERNAME**: Username for Netconf authentication.
- **NETCONF_PASSWORD**: Password for Netconf authentication.

### Telnet Configuration
- **TELNET_SERVER_ENABLED**: Enable Telnet server (default is false).
- **TELNET_USERNAME**: Telnet username.
- **TELNET_PASSWORD**: Telnet password.

### OpenAI Integration (Optional)
- **OPENAI_SUPPORT**: Enable OpenAI support for handling unknown commands (default is true).
- **OPENAI_APIKEY**: Set your OpenAI API key [here](https://platform.openai.com/).

### Logging Configuration
- **DEBUG_ENABLED**: Enable print debug logs (default is false)

## Device Configuration Management

Mock'it also includes a simple database management system for creating, reading, updating, and deleting device configurations. This makes it easier to manage and customize your device configurations.

For more details on how to use the database manager and create your own configuration logic, please check the YouTube video here:  
[Device Configuration Management Video](https://www.youtube.com/watch?v=fMtLNYJ3708&list=PLxv8A...)

## Conclusion

<<<<<<< README.md
Mock'it is a powerful tool that enables network professionals to test and automate network device interactions in a controlled environment. With extensive device support, customizable responses, and easy deployment, it’s a versatile solution for any network automation or simulation need.
=======
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
>>>>>>> README.md
