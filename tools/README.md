# Network Device Data Generator

A Python script that generates mock network device data for testing and development purposes. The script can generate various types of network data including routing tables, ARP entries, MAC address tables, and interface information.

## Features

- Generates realistic network device data
- Supports multiple data types:
  - IP Routes
  - ARP Entries
  - MAC Address Tables
  - Interface Status
- Configurable through settings.conf
- Supports multiple device types/platforms
- Distributes data across multiple devices

## Configuration (settings.conf)

The script is configured through `settings.conf`. Here's a sample configuration:

```ini
# Network Data Generator Configuration
# Use # for comments

# Platform name (leave it as cisco_ios)
platform = cisco_ios

# Data types to generate
# Available types: routes, arp, mac, interfaces
data_types = routes, arp, mac, interfaces

# Device separation settings
seperate_config_over_devices = true
seperate_devices = a10, cisco_ios, accedian, adtran_os

# Number of entries to generate for each data type
[counts]
routes = 100000
arp = 100000
mac = 100000
interfaces = 100000
```

### Configuration Options

- `platform`: Specifies the platform type (default: cisco_ios)
- `data_types`: Comma-separated list of data types to generate
- `seperate_config_over_devices`: Boolean to enable/disable data distribution across devices
- `seperate_devices`: List of device types to generate data for
- `counts`: Section defining the number of entries to generate for each data type

## Directory Structure

The script generates files in the following structure:
```
configs/
├── device1/
│   └── template/
│       ├── show ip route.txt
│       ├── show arp.txt
│       ├── show mac address-table.txt
│       └── show ip interface brief.txt
├── device2/
│   └── template/
│       └── ...
└── ...
```

## Usage

1. Configure the settings in `settings.conf`
2. Run the script:
```bash
python mock_data_generator.py
```

## Generated Data Types

### Routes
- Generates realistic IP routes with various protocols (OSPF, BGP, Static, etc.)
- Includes metrics and next-hop information
- Follows Cisco IOS format

### ARP Entries
- Generates ARP table entries with IP-to-MAC mappings
- Includes age information and interface associations
- Follows standard network device format

### MAC Address Table
- Generates MAC address entries with VLAN associations
- Includes both dynamic and static entries
- Associates entries with interfaces

### Interfaces
- Generates interface status information
- Includes IP addresses, status, and protocols
- Supports various interface types (Gigabit, FastEthernet, etc.)

## Notes

- The script automatically creates the settings file if it doesn't exist
- Large numbers of entries are handled efficiently with deterministic generation
- The script distributes entries evenly across configured devices
- All generated data follows realistic network device formatting

## Requirements

- Python 3.6 or higher
- No external dependencies required

## Limitations

- Generated data is mock data and should only be used for testing
- Very large numbers of entries may require additional memory
- Some interface combinations may be repeated with very large numbers
```

This README provides a comprehensive overview of the script's functionality, configuration options, and usage. Let me know if you'd like me to expand on any section or add additional information!
