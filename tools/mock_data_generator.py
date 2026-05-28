"""
Network Device Data Generator

Generates mock data for network devices including routing tables,
ARP entries, MAC address tables, interface information, and VRFs.
"""
import random
import os

def generate_ip(private_only=False, avoid_private=False):
    """Generate a random IP address with options to control the range."""
    if private_only:
        first_octet = random.choice([10, 172, 192])
        if first_octet == 10:
            return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        elif first_octet == 172:
            return f"172.{random.randint(16, 31)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        else:
            return f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"
    elif avoid_private:
        while True:
            first_octet = random.randint(1, 223)
            if first_octet not in [10, 172, 192]:
                return f"{first_octet}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    else:
        # Mix of private and public with preference for private
        if random.random() < 0.7:  # 70% chance of private IP
            return generate_ip(private_only=True)
        else:
            return generate_ip(avoid_private=True)


def generate_mac(cisco_format=True):
    """Generate a random MAC address in standard or Cisco format."""
    mac_bytes = [random.randint(0, 255) for _ in range(6)]
    if cisco_format:
        # Format as 0000.1111.2222
        return f"{mac_bytes[0]:02x}{mac_bytes[1]:02x}.{mac_bytes[2]:02x}{mac_bytes[3]:02x}.{mac_bytes[4]:02x}{mac_bytes[5]:02x}"
    else:
        # Format as 00:11:22:33:44:55
        return ':'.join(f"{b:02x}" for b in mac_bytes)


def generate_interface_name(allow_higher_numbers=False, unique_id=None):
    """Generate a random network interface name."""
    interface_types = [
        "GigabitEthernet",
        "TenGigabitEthernet",
        "FastEthernet",
        "Loopback",
        "VirtualPortGroup",
        "Port-channel",
        "Tunnel",
        "HundredGigE",
        "FortyGigE",
        "Ethernet",
        "Vlan",
        "Serial"
    ]
    
    # If we have a unique ID, use it to create deterministic unique interfaces
    if unique_id is not None:
        # Distribute unique_id across all interface types
        interface_type = interface_types[unique_id % len(interface_types)]
        
        if interface_type == "Loopback":
            return f"{interface_type}{unique_id}"
        elif interface_type == "VirtualPortGroup":
            return f"{interface_type}{unique_id % 1000}"
        elif interface_type == "Vlan":
            return f"{interface_type}{unique_id % 4094 + 1}"  # VLANs 1-4094
        else:
            chassis = (unique_id // 1000) % 100
            slot = (unique_id // 100) % 10
            module = (unique_id // 10) % 10
            port = unique_id % 48
            return f"{interface_type}{chassis}/{slot}/{module}/{port}"
    
    # Original random generation for smaller numbers
    interface_type = random.choice(interface_types)
    
    if interface_type == "Loopback":
        return f"{interface_type}{random.randint(0, 999)}"
    elif interface_type == "VirtualPortGroup":
        return f"{interface_type}{random.randint(0, 9)}"
    elif interface_type == "Vlan":
        return f"{interface_type}{random.randint(1, 4094)}"
    elif allow_higher_numbers:
        # Use higher numbers for high-volume generation
        chassis = random.randint(0, 9)
        slot = random.randint(0, 9)
        module = random.randint(0, 9)
        port = random.randint(0, 48)
        return f"{interface_type}{chassis}/{slot}/{module}/{port}"
    else:
        return f"{interface_type}{random.randint(1, 9)}"


def generate_vrf_names(vrf_name_format, count, fallback_format="03d"):
    """
    Generate a list of VRF names of exactly `count` total entries.

    vrf_name_format is a comma-separated string where each token is one of:
      - An exact name (no trailing underscore): used as-is, e.g. MGMT
      - A prefix (trailing underscore) with optional format= and weight= modifiers:
            CUST_ format=02d weight=3
        format= controls zero-padding of the numeric suffix (default: no padding, e.g. 1, 2, 3)
        weight= controls how many of the remaining slots this prefix gets relative to
                other prefixes (default: 1); remaining slots are divided proportionally

    After placing all fixed names and distributing remaining slots across prefixes by
    weight, any still-unfilled slots are padded with fallback names using fallback_format
    (e.g. "03d" -> 001, 002, 003 ...).

    Example:
      vrf_name_format = MGMT, PROD, CUST_ format=02d weight=3, TENANT_ format=04d weight=1
      count = 20, fallback_format = 03d
      -> MGMT, PROD (2 fixed), 18 remaining: CUST_ gets 14 (3/4), TENANT_ gets 4 (1/4)
      -> CUST_01..CUST_14, TENANT_0001..TENANT_0004
    """
    fixed = []
    prefixes = []  # list of (prefix, fmt, weight)

    tokens = [t.strip() for t in vrf_name_format.split(',') if t.strip()]
    for token in tokens:
        parts = token.split()
        name = parts[0]
        fmt = None
        weight = 1
        for part in parts[1:]:
            if part.startswith('format='):
                fmt = part.split('=', 1)[1]
            elif part.startswith('weight='):
                try:
                    weight = int(part.split('=', 1)[1])
                except ValueError:
                    weight = 1
        if name.endswith('_'):
            prefixes.append((name, fmt, weight))
        else:
            fixed.append(name)

    names = list(fixed)
    remaining = count - len(names)

    if remaining > 0 and prefixes:
        total_weight = sum(w for _, _, w in prefixes)
        # Distribute remaining slots proportionally by weight
        allotments = []
        distributed = 0
        for i, (prefix, fmt, weight) in enumerate(prefixes):
            if i == len(prefixes) - 1:
                # Last prefix gets whatever is left to avoid rounding shortfall
                allotments.append(remaining - distributed)
            else:
                n = (weight * remaining) // total_weight
                allotments.append(n)
                distributed += n

        for (prefix, fmt, weight), n in zip(prefixes, allotments):
            for i in range(1, n + 1):
                if fmt:
                    names.append(f"{prefix}{i:{fmt}}")
                else:
                    names.append(f"{prefix}{i}")

    # Pad with fallback names if still short
    fallback_i = 1
    while len(names) < count:
        candidate = f"{fallback_i:{fallback_format}}"
        if candidate not in names:
            names.append(candidate)
        fallback_i += 1

    return names[:count]


def generate_vrf_rd(index):
    """Generate a route distinguisher for a VRF."""
    asn = random.choice([65000, 65001, 65100, 100, 200])
    return f"{asn}:{100 + index}"


def generate_show_vrf(vrf_names):
    """Generate 'show vrf' output (brief table). Matches cisco_ios/templates/show vrf.txt style."""
    lines = ["Name                             Default RD            Protocols   Interfaces"]
    iface_types = ["Gi0/0", "Gi0/1", "Gi1", "Gi2", "Te0/0", "Lo"]
    for i, name in enumerate(vrf_names):
        rd = generate_vrf_rd(i)
        iface = f"{random.choice(iface_types)}.{100 + i}"
        lines.append(f"  {name:<33}{rd:<22}ipv4        {iface}")
    return "\n".join(lines)


def generate_show_vrf_detail(vrf_names):
    """Generate 'show vrf detail' output. Matches cisco_xe/templates/show vrf detail.txt style."""
    lines = []
    for i, name in enumerate(vrf_names):
        rd = generate_vrf_rd(i)
        vrf_id = i + 1
        rt_export = f"RT:{rd}"
        rt_import = f"RT:{generate_vrf_rd(i + 1)}"
        iface = f"Gi{random.randint(0, 3)}"
        lines += [
            f"VRF {name} (VRF Id = {vrf_id}); default RD {rd}; default VPNID <not set>",
            "  Old CLI format, supports IPv4 only",
            "  Flags: 0xC",
            "  Interfaces:",
            f"    {iface}                     ",
            "Address family ipv4 unicast (Table ID = 0x{:X}):".format(vrf_id),
            "  Flags: 0x0",
            "  Export VPN route-target communities",
            f"    {rt_export}             ",
            "  Import VPN route-target communities",
            f"    {rt_import}",
            "  No import route-map",
            "  No global export route-map",
            "  No export route-map",
            "  VRF label distribution protocol: not configured",
            "  VRF label allocation mode: per-prefix",
            "Address family ipv6 unicast not active",
            "Address family ipv4 multicast not active",
            "Address family ipv6 multicast not active",
            "",
        ]
    return "\n".join(lines)


def generate_show_ip_vrf_interfaces(vrf_names):
    """Generate 'show ip vrf interfaces'. Matches cisco_ios/templates/show ip vrf interfaces.txt style."""
    lines = ["Interface              IP-Address      VRF                              Protocol"]
    iface_prefixes = ["GigabitEthernet", "TenGigabitEthernet", "FastEthernet", "Loopback"]
    for i, name in enumerate(vrf_names):
        iface = f"{random.choice(iface_prefixes)}{random.randint(0, 4)}/{random.randint(0, 1)}"
        ip = generate_ip(private_only=True)
        proto = "up" if random.random() > 0.1 else "down"
        lines.append(f"{iface:<23}{ip:<16}{name:<33}{proto}")
    return "\n".join(lines)


def generate_vrf_routes(vrf_name, num_routes):
    """Generate 'show ip route vrf <name>' output."""
    protocols = {
        'O': '[110/2] via',
        'B': '[200/0] via',
        'D': '[90/2] via',
        'S': '[1/0] via',
        'R': '[120/1] via',
        'E1': '[110/3] via',
        'E2': '[110/1] via',
    }
    interfaces = [
        'GigabitEthernet1', 'GigabitEthernet2', 'GigabitEthernet3',
        'TenGigabitEthernet1', 'FastEthernet0/0', 'FastEthernet0/1'
    ]
    header_lines = [
        f"Routing Table: {vrf_name}",
        "Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP",
        "       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area",
        "       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2",
        "       E1 - OSPF external type 1, E2 - OSPF external type 2",
        "",
        "Gateway of last resort is not set",
        "",
    ]
    routes = []
    used_networks = set()
    for _ in range(num_routes):
        while True:
            first_octet = random.randint(1, 223)
            if first_octet not in [10, 172, 192]:
                network = f"{first_octet}.{random.randint(0, 255)}.{random.randint(0, 255)}.0"
                mask = random.randint(24, 30)
                network_with_mask = f"{network}/{mask}"
                if network_with_mask not in used_networks:
                    used_networks.add(network_with_mask)
                    break
        next_hop = f"10.10.{random.randint(1, 254)}.{random.randint(1, 254)}"
        protocol = random.choice(list(protocols.keys()))
        metric_info = protocols[protocol]
        interface = random.choice(interfaces)
        routes.append(f"{protocol}     {network_with_mask} {metric_info} {next_hop}, {interface}")
    return "\n".join(header_lines + routes)


def process_vrfs(base_dir, vrf_name_format, count, fallback_format="03d", min_routes_per_vrf=50, max_routes_per_vrf=1000):
    """
    Generate all VRF-related template files.

    Always writes:
      - show vrf.txt
      - show vrf detail.txt
      - show ip vrf interfaces.txt

    Writes per-VRF route files only when max_routes_per_vrf > 0:
      - show ip route vrf <name>.txt
    """
    vrf_names = generate_vrf_names(vrf_name_format, count, fallback_format)

    write_file(
        os.path.join(base_dir, "show vrf.txt"),
        generate_show_vrf(vrf_names)
    )
    write_file(
        os.path.join(base_dir, "show vrf detail.txt"),
        generate_show_vrf_detail(vrf_names)
    )
    write_file(
        os.path.join(base_dir, "show ip vrf interfaces.txt"),
        generate_show_ip_vrf_interfaces(vrf_names)
    )

    if max_routes_per_vrf > 0:
        for name in vrf_names:
            num_routes = random.randint(min_routes_per_vrf, max_routes_per_vrf)
            content = generate_vrf_routes(name, num_routes)
            write_file(
                os.path.join(base_dir, f"show ip route vrf {name}.txt"),
                content
            )
        print(f"Successfully generated VRF data for {len(vrf_names)} VRFs (with per-VRF routes)")
    else:
        print(f"Successfully generated VRF data for {len(vrf_names)} VRFs (no per-VRF routes)")

    return "vrfs"


def generate_routes(num_routes=200000):
    """Generate routing table entries."""
    # Protocol definitions
    protocols = {
        'O': '[110/2] via',
        'B': '[200/0] via',
        'D': '[90/2] via',
        'S': '[1/0] via',
        'R': '[120/1] via',
        'E1': '[110/3] via',
        'E2': '[110/1] via',
        'N1': '[110/2] via',
        'N2': '[110/2] via'
    }
    
    # Common next-hop interfaces
    interfaces = [
        'GigabitEthernet1',
        'GigabitEthernet2',
        'GigabitEthernet3',
        'TenGigabitEthernet1',
        'FastEthernet0/0',
        'FastEthernet0/1'
    ]
    
    routes = []
    used_networks = set()  # To avoid duplicate networks
    
    for _ in range(num_routes):
        # Generate random network (avoiding RFC1918 for variety)
        while True:
            first_octet = random.randint(1, 223)
            if first_octet not in [10, 172, 192]:  # Avoid private ranges
                network = f"{first_octet}.{random.randint(0, 255)}.{random.randint(0, 255)}.0"
                mask = random.randint(24, 30)  # Common subnet masks
                network_with_mask = f"{network}/{mask}"
                
                if network_with_mask not in used_networks:
                    used_networks.add(network_with_mask)
                    break
        
        # Generate random next-hop IP
        next_hop = f"10.10.{random.randint(1, 254)}.{random.randint(1, 254)}"
        
        # Select random protocol and its metric
        protocol = random.choice(list(protocols.keys()))
        metric_info = protocols[protocol]
        
        # Select random interface
        interface = random.choice(interfaces)
        
        # Create route entry
        route = f"{protocol}     {network_with_mask} {metric_info} {next_hop}, {interface}"
        routes.append(route)
    
    return routes


def generate_arp_entries(num_entries=1000):
    """Generate ARP table entries based on Cisco IOS format."""
    arp_entries = []
    
    # Add header
    arp_entries.append("Protocol  Address          Age (min)  Hardware Addr   Type   Interface")
    
    # Generate random ARP entries
    for _ in range(num_entries):
        # Generate IP address (mostly in 10.x.x.x range)
        ip = generate_ip()
        
        # Generate MAC address in Cisco format
        mac = generate_mac(cisco_format=True)
        
        # Generate age (some percentage will be interface entries with "-")
        age = "-" if random.random() < 0.2 else str(random.randint(0, 999))
        
        # Interface type and number
        interface = generate_interface_name()
        
        # Format the entry with proper spacing
        entry = f"Internet  {ip.ljust(15)}  {age.rjust(12)}   {mac}  ARPA   {interface}"
        arp_entries.append(entry)
    
    return arp_entries


def generate_mac_entries(num_entries=1000):
    """Generate MAC address table entries."""
    mac_entries = []
    
    # Add header
    mac_entries.append("          Mac Address Table")
    mac_entries.append("-------------------------------------------")
    mac_entries.append("")
    mac_entries.append("Vlan    Mac Address       Type        Ports")
    mac_entries.append("----    -----------       --------    -----")
    
    # Generate random MAC entries
    for _ in range(num_entries):
        # Generate VLAN ID
        vlan = random.randint(1, 4094)
        
        # Generate MAC address
        mac = f"{random.randint(0, 255):02x}{random.randint(0, 255):02x}.{random.randint(0, 255):02x}{random.randint(0, 255):02x}.{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
        
        # Type (mostly DYNAMIC with some STATIC)
        entry_type = "DYNAMIC" if random.random() < 0.95 else "STATIC"
        
        # Interface types
        interface_types = [
            "Gi1/0/",
            "Gi2/0/",
            "Te1/1/",
            "Po"
        ]
        
        interface_type = random.choice(interface_types)
        if interface_type == "Po":
            interface = f"{interface_type}{random.randint(1, 48)}"
        else:
            interface = f"{interface_type}{random.randint(1, 48)}"
        
        # Format the entry
        entry = f"{vlan:<8} {mac:<17} {entry_type:<12} {interface}"
        mac_entries.append(entry)
    
    # Add footer
    mac_entries.append("")
    mac_entries.append(f"Total Mac Addresses for this criterion: {num_entries}")
    
    return mac_entries


def generate_interfaces(num_entries=50):
    """Generate interface status entries based on Cisco IOS format."""
    interface_entries = []
    
    # Add header
    interface_entries.append("Interface              IP-Address      OK? Method Status                Protocol")
    
    # Status options
    statuses = ["up", "administratively down", "down"]
    protocols = ["up", "down"]
    methods = ["NVRAM", "unset", "DHCP", "manual"]
    
    # For very large numbers, use deterministic generation instead of random with duplicates check
    if num_entries > 20000:
        # Generate each interface with a unique ID (silently)
        for i in range(num_entries):
            # Generate interface name using the unique ID
            interface = generate_interface_name(allow_higher_numbers=True, unique_id=i)
            
            # Generate IP address (some percentage will be unassigned)
            if random.random() < 0.3:  # 30% chance of being unassigned
                ip = "unassigned"
            else:
                ip = generate_ip()
            
            # Generate OK status (almost always YES)
            ok = "YES" if random.random() < 0.98 else "NO"
            
            # Generate method
            method = random.choice(methods)
            
            # Generate status and protocol
            status = random.choice(statuses)
            # If status is not "up", protocol is likely "down"
            protocol = "down" if status != "up" or random.random() < 0.2 else "up"
            
            # Format the entry with proper spacing
            entry = f"{interface.ljust(22)} {ip.ljust(15)} {ok.ljust(3)} {method.ljust(6)} {status.ljust(20)} {protocol}"
            interface_entries.append(entry)
        
        return interface_entries
    
    # Original implementation for smaller numbers
    generated_interfaces = set()  # Use a set for faster lookups
    
    # Determine if we need to allow higher interface numbers
    max_standard_interfaces = 1037  # Approximate count of interfaces with standard naming
    allow_higher_numbers = num_entries > max_standard_interfaces
    
    # Keep generating until we have the requested number of entries or hit the limit
    attempt_count = 0
    max_attempts = num_entries * 10  # Prevent infinite loops
    
    while len(generated_interfaces) < num_entries and attempt_count < max_attempts:
        attempt_count += 1
        
        # Generate interface name
        interface = generate_interface_name(allow_higher_numbers)
        
        # Check if this interface already exists
        if interface in generated_interfaces:
            continue
        
        generated_interfaces.add(interface)
        
        # Generate IP address (some percentage will be unassigned)
        if random.random() < 0.3:  # 30% chance of being unassigned
            ip = "unassigned"
        else:
            ip = generate_ip()
        
        # Generate OK status (almost always YES)
        ok = "YES" if random.random() < 0.98 else "NO"
        
        # Generate method
        method = random.choice(methods)
        
        # Generate status and protocol
        status = random.choice(statuses)
        # If status is not "up", protocol is likely "down"
        protocol = "down" if status != "up" or random.random() < 0.2 else "up"
        
        # Format the entry with proper spacing
        entry = f"{interface.ljust(22)} {ip.ljust(15)} {ok.ljust(3)} {method.ljust(6)} {status.ljust(20)} {protocol}"
        interface_entries.append(entry)
    
    return interface_entries


def write_file(filepath, content):
    """Write content to file and create directory if needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Output written to: {filepath}")


def load_settings():
    """Load settings from settings.conf file."""
    settings_file = os.path.join(os.path.dirname(__file__), "settings.conf")
    
    # Default settings
    default_settings = {
        "platform": "cisco_ios",
        "data_types": ["routes", "arp", "mac", "interfaces"],
        "seperate_config_over_devices": False,
        "devices": ["cisco_ios"],
        "counts": {
            "routes": 1000,
            "arp": 1000,
            "mac": 1000,
            "interfaces": 1000
        },
        "vrfs": {
            "count": 10,
            "vrf_name_format": "MGMT, PROD, CUST_ format=02d weight=3, TENANT_ format=04d weight=1",
            "fallback_format": "03d",
            "min_routes_per_vrf": 50,
            "max_routes_per_vrf": 1000
        }
    }
    
    # Check if settings file exists
    if os.path.exists(settings_file):
        try:
            settings = default_settings.copy()
            current_section = None
            
            with open(settings_file, 'r') as f:
                for line in f:
                    # Skip comments and empty lines
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Check for section headers
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        print("current_section", current_section)
                        if current_section not in settings:
                            settings[current_section] = {}
                        continue
                    
                    # Parse key-value pairs
                    if '=' in line:
                        key, value = [x.strip() for x in line.split('=', 1)]
                        
                        if current_section:
                            # Handle section values
                            if key in default_settings.get(current_section, {}):
                                try:
                                    # Try to convert to int if it's a count
                                    settings[current_section][key] = int(value)
                                except ValueError:
                                    settings[current_section][key] = value
                        else:
                            # Handle top-level values
                            if key == "data_types":
                                # Split comma-separated list
                                settings[key] = [x.strip() for x in value.split(',')]
                            elif key == "devices":
                                # Parse the list from string, handling quotes and brackets
                                value = value.strip('[]')
                                settings[key] = [x.strip().strip('"\'') for x in value.split(',')]
                            elif key == "seperate_config_over_devices":
                                settings[key] = value.lower() == 'true'
                            elif key in default_settings:
                                settings[key] = value
            
            return settings
                
        except Exception as e:
            print(f"Error loading settings: {e}")
            print(f"Using default settings instead")
            return default_settings
    else:
        # Create default settings file
        try:
            with open(settings_file, 'w') as f:
                f.write("# Network Data Generator Configuration\n")
                f.write("# Use # for comments\n\n")
                
                # Write platform
                f.write(f"# Platform name (determines output directory)\n")
                f.write(f"platform = {default_settings['platform']}\n\n")
                
                # Write data types
                f.write(f"# Data types to generate (comma-separated list)\n")
                f.write(f"# Available types: routes, arp, mac, interfaces\n")
                f.write(f"data_types = {','.join(default_settings['data_types'])}\n\n")
                
                # Write device separation settings
                f.write(f"seperate_config_over_devices = {str(default_settings['seperate_config_over_devices']).lower()}\n")
                f.write(f"devices = {default_settings['devices']}\n\n")
                
                # Write counts
                f.write(f"# Number of entries to generate for each data type\n")
                f.write(f"[counts]\n")
                for key, value in default_settings['counts'].items():
                    f.write(f"{key} = {value}\n")
                
            print(f"Created default settings file: {settings_file}")
        except Exception as e:
            print(f"Error creating settings file: {e}")
        
        return default_settings


def process_routes(base_dir, num_routes):
    """Process and generate routing table entries."""
    routes = generate_routes(num_routes)
    header="Gateway of last resort is not set\n\n"
    # Create new content with header and new routes
    new_content = header + "\n".join(routes)
    
    template_file = os.path.join(base_dir, "show ip route.txt")

    # Write to file
    write_file(template_file, new_content)
    
    print(f"Successfully generated {len(routes)} routes")
    return "routes"


def process_arp(base_dir, num_arp):
    """Process and generate ARP entries."""
    arp_entries = generate_arp_entries(num_arp)
    
    # Write to file
    template_file = os.path.join(base_dir, "show arp.txt")
    write_file(template_file, "\n".join(arp_entries))
    
    print(f"Successfully generated {num_arp} ARP entries")
    return "arp"


def process_mac(base_dir, num_mac):
    """Process and generate MAC address table entries."""
    mac_entries = generate_mac_entries(num_mac)
    
    # Write to file
    template_file = os.path.join(base_dir, "show mac address-table.txt")
    write_file(template_file, "\n".join(mac_entries))
    
    print(f"Successfully generated {num_mac} MAC entries")
    return "mac"


def process_interfaces(base_dir, num_interfaces):
    """Process and generate interface entries."""
    interface_entries = generate_interfaces(num_interfaces)
    
    # Write to file
    template_file = os.path.join(base_dir, "show ip interface brief.txt")
    write_file(template_file, "\n".join(interface_entries))
    
    print(f"Successfully generated {len(interface_entries)-1} interface entries")  # -1 for header
    return "interfaces"

def generate_docker_compose(device_list, platform, base_dir):
    """Generate docker-compose.yml file for the devices."""
    compose_content = [
        "name: devices",
        "services:"
    ]
    
    # Generate service for each device
    for i, device in enumerate(device_list, 1):
        
        service = f"""  {device}:
    image: registry.gitlab.com/slurpit.io/mockit:latest
    container_name: {device}
    environment:
      - DEVICE_TYPE={platform}
      - SSH_USERNAME=test
      - SSH_PASSWORD=test
      - NETCONF_USERNAME=test
      - NETCONF_PASSWORD=test
      - TELNET_USERNAME=test
      - TELNET_PASSWORD=test
      - DEBUG_ENABLED=true
    volumes:
      - ./{device}/configs/{platform}:/configs/{platform}/templates"""
        compose_content.append(service)
    
    # Add network configuration at the end
    compose_content.append("""networks:
  devices_network:
    driver: bridge
    """)
    
    # Write to docker-compose.yml
    with open(base_dir + '/docker-compose.yml', 'w') as f:
        f.write('\n'.join(compose_content))
    
    print("Generated docker-compose.yml file")

def clean_output_directory():
    """Delete the existing output directory if it exists."""
    output_dir = "./output"
    if os.path.exists(output_dir):
        import shutil
        try:
            shutil.rmtree(output_dir)
            print(f"Deleted existing output directory: {output_dir}")
        except Exception as e:
            print(f"Error deleting output directory: {e}")

def main():
    """Main function to orchestrate data generation based on settings."""
    # Clean existing output directory
    clean_output_directory()
    
    # Load settings
    settings = load_settings()
    
    # Get platform and data types
    platform = settings.get("platform", "cisco_ios")
    # Currently we only support cisco_ios
    if platform != "cisco_ios":
        platform = "cisco_ios"

    data_types = settings.get("data_types", ["routes"])
    device_list = settings.get("devices", ["cisco_ios"])
    seperate_config_over_devices = settings.get("seperate_config_over_devices", False)
    routes_count = settings.get("counts", {}).get("routes", 1000)
    arp_count = settings.get("counts", {}).get("arp", 1000)
    mac_count = settings.get("counts", {}).get("mac", 1000)
    interfaces_count = settings.get("counts", {}).get("interfaces", 1000)
    vrf_count = settings.get("vrfs", {}).get("count", 10)
    vrf_name_format = settings.get("vrfs", {}).get("vrf_name_format", "MGMT, PROD, CUST_ format=02d weight=3, TENANT_ format=04d weight=1")
    vrf_fallback_format = settings.get("vrfs", {}).get("fallback_format", "03d")
    min_routes_per_vrf = settings.get("vrfs", {}).get("min_routes_per_vrf", 50)
    max_routes_per_vrf = settings.get("vrfs", {}).get("max_routes_per_vrf", 1000)
    device_count = len(device_list)
    
    print(f"Device count: {device_count}")
    if seperate_config_over_devices:
        # Process for each device
        for i, device in enumerate(device_list, 1):
            # Create device-specific base directory
            base_dir = f"./output/{device}/configs/{platform}"
            
            # Ensure directory exists
            os.makedirs(base_dir, exist_ok=True)
            
            print(f"\nProcessing device {i}...")
            
            # Process each data type
            processed_types = []
            device_processors = {}
            # Define processor mapping with adjusted counts for each device
            if i == device_count:
                # handle the last device
                device_processors = {
                    "routes": lambda: process_routes(base_dir, routes_count - (routes_count // device_count) * (device_count - 1)),
                    "arp": lambda: process_arp(base_dir, arp_count - (arp_count // device_count) * (device_count - 1)),
                    "mac": lambda: process_mac(base_dir, mac_count - (mac_count // device_count) * (device_count - 1)),
                    "interfaces": lambda: process_interfaces(base_dir, interfaces_count - (interfaces_count // device_count) * (device_count - 1)),
                    "vrfs": lambda: process_vrfs(base_dir, vrf_name_format, vrf_count, vrf_fallback_format, min_routes_per_vrf, max_routes_per_vrf)
                }
            else:
                device_processors = {
                    "routes": lambda: process_routes(base_dir, routes_count // device_count),
                    "arp": lambda: process_arp(base_dir, arp_count // device_count),
                    "mac": lambda: process_mac(base_dir, mac_count // device_count),
                    "interfaces": lambda: process_interfaces(base_dir, interfaces_count // device_count),
                    "vrfs": lambda: process_vrfs(base_dir, vrf_name_format, vrf_count, vrf_fallback_format, min_routes_per_vrf, max_routes_per_vrf)
                }
            
            # Process each requested data type
            for data_type in data_types:
                if data_type in device_processors:
                    processed_types.append(device_processors[data_type]())
                else:
                    print(f"Unknown data type: {data_type}")
            
            print(f"{device} Summary: Generated data for {', '.join(processed_types)}")
        
        print("\nAll devices processed successfully!")
    else:
        for i, device in enumerate(device_list, 1):
            # Create device-specific base directory
            base_dir = f"./output/{device}/configs/{platform}"
            
            # Ensure directory exists
            os.makedirs(base_dir, exist_ok=True)
            
            print(f"\nProcessing device {i}...")
            
            # Process each data type
            processed_types = []
            device_processors = {}
            device_processors = {
                "routes": lambda: process_routes(base_dir, routes_count),
                "arp": lambda: process_arp(base_dir, arp_count),
                "mac": lambda: process_mac(base_dir, mac_count),
                "interfaces": lambda: process_interfaces(base_dir, interfaces_count),
                "vrfs": lambda: process_vrfs(base_dir, vrf_name_format, vrf_count, vrf_fallback_format, min_routes_per_vrf, max_routes_per_vrf)
            }
            
            # Process each requested data type
            for data_type in data_types:
                if data_type in device_processors:
                    processed_types.append(device_processors[data_type]())
                else:
                    print(f"Unknown data type: {data_type}")
            
            print(f"{device} Summary: Generated data for {', '.join(processed_types)}")
        
        print("\nAll devices processed successfully!")

    # Generate docker-compose.yml after processing all devices
    generate_docker_compose(device_list, platform, "./output")


if __name__ == "__main__":
    main()