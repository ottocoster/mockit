# mockit tools

## Network Device Data Generator

A Python script that generates mock network device data for testing and development purposes. The script can generate various types of network data including routing tables, ARP entries, MAC address tables, interface information, and VRFs.

### Features

- Generates realistic network device data
- Supports multiple data types:
  - IP Routes
  - ARP Entries
  - MAC Address Tables
  - Interface Status
  - VRFs (with optional per-VRF route tables)
- Configurable through settings.conf
- Supports multiple device types/platforms
- Distributes data across multiple devices

### Configuration (settings.conf)

The script is configured through `settings.conf`. Here's a sample configuration:

```ini
# Network Data Generator Configuration
# Use # for comments

# Platform name (leave it as cisco_ios)
platform = cisco_ios

# Data types to generate
# Available types: routes, arp, mac, interfaces, vrfs
data_types = routes, arp, mac, interfaces, vrfs

# Device separation settings
seperate_config_over_devices = true
seperate_devices = a10, cisco_ios, accedian, adtran_os

# Number of entries to generate for each data type
[counts]
routes = 100000
arp = 100000
mac = 100000
interfaces = 100000

# VRF settings
[vrfs]
count = 10
vrf_name_format = MGMT, PROD, CUST_ format=02d weight=3, TENANT_ format=04d weight=1
fallback_format = 03d
min_routes_per_vrf = 50
max_routes_per_vrf = 1000
```

#### Configuration Options

- `platform`: Specifies the platform type (default: cisco_ios)
- `data_types`: Comma-separated list of data types to generate
- `seperate_config_over_devices`: Boolean to enable/disable data distribution across devices
- `seperate_devices`: List of device types to generate data for
- `counts`: Section defining the number of entries to generate for each data type
- `vrfs`: Section defining VRF generation behaviour (see below)

#### VRF Configuration (`[vrfs]`)

- `count`: Total number of VRFs to generate
- `vrf_name_format`: Comma-separated list of VRF name specifications:
  - Plain names (e.g. `MGMT`, `VRF_A`) are used exactly as written and count toward the total
  - Prefix names (trailing `_`, e.g. `CUST_`, `TENANT_`) fill the remaining slots after fixed names, distributed proportionally by `weight=`
  - `format=` controls zero-padding of the numeric suffix (e.g. `format=02d` → `CUST_01`, `format=04d` → `TENANT_0001`); omit for no padding
  - `weight=` controls how many of the remaining slots a prefix gets relative to other prefixes (default: `1`, i.e. equal share)
  - Any slots still unfilled after all prefixes are exhausted are padded with plain numbers using `fallback_format`
- `fallback_format`: Python format spec for fallback VRF names when prefix slots don't reach `count` (default: `03d` → `001, 002, 003 ...`)
- `min_routes_per_vrf`: Minimum routes to generate in each per-VRF route file (default: 50; set to 0 to potentially have some VRFs with no routes)
- `max_routes_per_vrf`: Maximum routes to generate in each per-VRF route file (default: 1000; set to 0 to skip per-VRF route creation entirely)

### Directory Structure

The script generates files in the following structure:
```
output/
├── device1/
│   └── configs/
│       └── cisco_ios/
│           ├── show ip route.txt
│           ├── show arp.txt
│           ├── show mac address-table.txt
│           ├── show ip interface brief.txt
│           ├── show vrf.txt
│           ├── show vrf detail.txt
│           ├── show ip vrf interfaces.txt
│           └── show ip route vrf <name>.txt  (one per VRF, if routes enabled)
├── device2/
│   └── ...
└── docker-compose.yml
```

### Usage

1. Configure the settings in `settings.conf`
2. Run the script:
```bash
python mock_data_generator.py
```

### Generated Data Types

#### Routes
- Generates realistic IP routes with various protocols (OSPF, BGP, Static, etc.)
- Includes metrics and next-hop information
- Follows Cisco IOS format

#### ARP Entries
- Generates ARP table entries with IP-to-MAC mappings
- Includes age information and interface associations
- Follows standard network device format

#### MAC Address Table
- Generates MAC address entries with VLAN associations
- Includes both dynamic and static entries
- Associates entries with interfaces

#### Interfaces
- Generates interface status information
- Includes IP addresses, status, and protocols
- Supports various interface types (Gigabit, FastEthernet, etc.)

#### VRFs
- Generates `show vrf`, `show vrf detail`, and `show ip vrf interfaces` output
- Optionally generates `show ip route vrf <name>` files for each VRF
- VRF names are fully configurable via `vrf_name_format`

### Notes

- The script automatically creates the settings file if it doesn't exist
- Large numbers of entries are handled efficiently with deterministic generation
- The script distributes entries evenly across configured devices
- All generated data follows realistic network device formatting

### Requirements

- Python 3.6 or higher
- No external dependencies required

### Limitations

- Generated data is mock data and should only be used for testing
- Very large numbers of entries may require additional memory
- Some interface combinations may be repeated with very large numbers

---

## Testing ssh KEX algorithms and ciphers

The `tools/test_ssh_algorithms.sh` script tests each specified KEX algorithm and cipher individually against a running mockit container. 

A `PASS` means the server accepted the negotiation (KEX succeeded, auth failed as expected with no credentials). 
A `FAIL` means the server rejected the algorithm during negotiation.

Only standard `ssh` (OpenSSH) is required — no `sshpass` or other tools needed.

```bash
# macOS: ssh is built in, nothing to install
# Debian/Ubuntu:
apt-get install openssh-client
```

**Basic usage (against local mockit on port 22):**
```bash
chmod +x tools/test_ssh_algorithms.sh
./tools/test_ssh_algorithms.sh
```

**Test specific KEX algorithms only:**
```bash
./tools/test_ssh_algorithms.sh --kex-only --kex "diffie-hellman-group1-sha1,diffie-hellman-group14-sha256,ecdh-sha2-nistp256"
```

**Test specific ciphers only:**
```bash
./tools/test_ssh_algorithms.sh --ciphers-only --ciphers "aes128-ctr,aes256-ctr,3des-cbc,chacha20-poly1305@openssh.com"
```

**Test against a remote/non-default host:**
```bash
./tools/test_ssh_algorithms.sh -h 172.16.240.45 -p 22 -u test
```

---

### Using ssh-audit (as a container)

[ssh-audit](https://github.com/jtesta/ssh-audit) is the most thorough way to enumerate exactly what a server advertises.

```bash
# Pull the image once
docker pull ghcr.io/jtesta/ssh-audit:latest

# Run against your mockit container
# Replace 172.16.240.45 with your container's IP (or host.docker.internal if on the same machine)
docker run --rm   --network devices_network   ghcr.io/jtesta/ssh-audit:latest   172.16.240.45

# To test only specific algorithms, combine with -j (JSON output) for scripting:
docker run --rm   --network devices_network   ghcr.io/jtesta/ssh-audit:latest   -j 172.16.240.45 | python3 -m json.tool
```

> The `--network devices_network` flag connects ssh-audit to the same Docker bridge
> network as mockit so it can reach the container's IP directly. The network name
> matches the one defined in `docker-compose.yml`; adjust if you've renamed it.

---

#### Using nmap (as a container)

```bash
# Pull the image once
docker pull instrumentisto/nmap:latest

# Enumerate all advertised SSH algorithms
docker run --rm   --network devices_network   instrumentisto/nmap:latest   --script ssh2-enum-algos   -p 22 172.16.240.45

# Broader SSH audit (version detection + algorithm enumeration)
docker run --rm   --network devices_network   instrumentisto/nmap:latest   -sV --script "ssh2-enum-algos,ssh-hostkey"   -p 22 172.16.240.45
```

---

#### Running everything locally (step by step)

**1. Build and start mockit with the algorithms you want to test:**
```bash
# Edit docker-compose.dev.yml to set your desired SSH_KEX_ALGORITHMS and SSH_CIPHERS, then:
docker compose -f docker-compose.dev.yml up --build -d
```

**2. Confirm the container is up and get its IP:**
```bash
docker compose -f docker-compose.dev.yml ps
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_name>
```

**3. Run the test script from the repo root:**
```bash
./tools/test_ssh_algorithms.sh -h <container_ip>
# or against localhost if port 22 is mapped to the host:
./tools/test_ssh_algorithms.sh
```

**4. Run ssh-audit as a container on the same network:**
```bash
docker run --rm --network devices_network ghcr.io/jtesta/ssh-audit:latest <container_ip>
```

**5. Run nmap as a container on the same network:**
```bash
docker run --rm --network devices_network instrumentisto/nmap:latest --script ssh2-enum-algos -p 22 <container_ip>
```

**6. Test a specific algorithm manually with plain ssh:**
```bash
# This should SUCCEED if the algorithm is in SSH_KEX_ALGORITHMS
# (you will get "Permission denied" — that means KEX worked):
ssh -F /dev/null -o KexAlgorithms=diffie-hellman-group14-sha256 -o NumberOfPasswordPrompts=0 -o StrictHostKeyChecking=no test@<container_ip>

# This should FAIL silently (no output) if it's NOT in SSH_KEX_ALGORITHMS:
ssh -F /dev/null -o KexAlgorithms=diffie-hellman-group1-sha1 -o NumberOfPasswordPrompts=0 -o StrictHostKeyChecking=no test@<container_ip>

# Similarly for ciphers:
ssh -F /dev/null -o Ciphers=aes256-ctr -o NumberOfPasswordPrompts=0 -o StrictHostKeyChecking=no test@<container_ip>
```

> Note: `-F /dev/null` ignores your local `~/.ssh/config` which could otherwise
> override algorithm choices and produce misleading results.

**7. Tear down:**
```bash
docker compose -f docker-compose.dev.yml down
```

