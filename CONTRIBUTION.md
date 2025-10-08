# Contributing to Mock'it

Thank you for your interest in contributing to Mock'it! This project is a powerful network device emulator that supports SSH, SNMP, Telnet, and Netconf protocols, currently supporting 115+ different network vendors. Your contributions help make this tool more comprehensive and useful for the networking community.

## Getting Started

Before contributing, please:

1. Fork the repository on GitLab
2. Clone your fork locally
3. Set up the development environment (see [Development Setup](#development-setup))
4. Read this guide thoroughly
5. Check existing issues to see if your contribution is already being worked on

## Types of Contributions

We welcome various types of contributions:

### Adding New Device Support
- Add support for network devices not currently supported
- Contribute SNMP walk data for devices missing SNMP support
- Add Netconf configuration templates for controller-based devices

### Improving Existing Devices
- Add missing command responses for existing devices
- Create Python logic for complex command handling
- Add support for different versions of existing devices
- Fix issues with existing device emulations

### Testing and Quality
- Write tests for new or existing functionality
- Report issues you encounter
- Optimize existing code

### Documentation
- Document device-specific configurations
- Create guides for common use cases
- Provide real-world usage examples

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.8+ (for local development)
- Git

### Local Development Environment

1. Clone the repository:
   ```bash
   git clone https://gitlab.com/slurpit.io/mockit.git
   cd mockit
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up development environment:
   ```bash
   # Configure git hooks for version management
   git config core.hooksPath .githooks
   ```

4. Test the setup:
   ```bash
   # Run basic tests
   cd tests
   docker compose -f compose-dev_ssh_telnet.yml up -d --build
   docker exec devices-test_container sh -c "pytest test_ssh_telnet.py -v"
   docker compose -f compose-dev_ssh_telnet.yml down
   ```

## Adding New Device Support

### 1. SSH/Telnet Device Support

#### Step 1: Create Device Directory Structure
```bash
mkdir -p configs/your_device_type/{templates,scripts,netconf}
```

#### Step 2: Add Command Templates
Create static command responses in `configs/your_device_type/templates/`:
- Each file should be named exactly as the command (e.g., `show version`)
- File content should be the pure output (no command prompt)
- Example: `configs/your_device_type/templates/show version`

#### Step 3: Add Dynamic Scripts (Optional)
Create `configs/your_device_type/scripts/__init__.py` for complex logic:
```python
def handle_command(command: str):
    if command.startswith('show interface'):
        # Your dynamic logic here
        return "Interface output here"
    return ""
```

#### Step 4: Add Device to Supported Lists
- Add device name to `supported_devices_ssh.md`
- Add device name to `supported_devices_telnet.md` (if telnet supported)

#### Step 5: Test Your Device
```bash
# Test SSH
docker compose up -d --build
ssh test@localhost -p 22

# Test Telnet (if supported)
telnet localhost 23
```

### 2. SNMP Device Support

#### Step 1: Gather SNMP Data
Use `snmpwalk` to collect SNMP data from a real device:
```bash
# Linux
snmpwalk -v2c -c public <device_ip> > snmp_output.txt

# Windows
snmpwalk -v:"2" -c:"public" -r:"<device_ip>" > snmp_output.txt
```

#### Step 2: Create SNMP Configuration
Create `configs/your_device_type/snmp.json` with the collected data.

#### Step 3: Add to Supported List
Add device name to `supported_devices_snmp.md`.

### 3. Netconf Device Support

#### Step 1: Create Netconf Template
Create `configs/your_device_type/netconf/get-config.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc-reply message-id="{message_id}"
    xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <!-- Your device configuration here -->
    </data>
</rpc-reply>
```

## Improving Existing Devices

### Adding New Commands
1. Static Commands: Add new files to `templates/` directory
2. Dynamic Commands: Modify `scripts/__init__.py` to handle new commands

### Adding Version Support
1. Create version-specific directory: `configs/device_type/version_name/`
2. Copy existing templates and modify as needed
3. Use `DEVICE_VERSION` environment variable to switch versions

### Using Database Operations
For complex state management, use the built-in database operations:
```python
from src.ssh_server.db_operations import create_table, create_record, read_record, update_record, delete_record

# Create a table for your device
create_table('your_device_type')

def handle_command(command: str):
    if command.startswith('vlan'):
        # Your VLAN management logic
        create_record('your_device_type', 'vlan', 'vlan_data')
        return "VLAN created"
```

## Testing Your Changes

### Running Tests
```bash
cd tests

# Test SSH and Telnet
docker compose -f compose-dev_ssh_telnet.yml up -d --build
docker exec devices-test_container sh -c "pytest test_ssh_telnet.py -v"

# Test SNMP
docker compose -f docker-compose.yml up -d --build
docker exec devices-test_container sh -c "pytest test_snmp.py -v"

# Test Netconf
docker exec devices-test_container sh -c "pytest test_netconf.py -v"

# Clean up
docker compose -f compose-dev_ssh_telnet.yml down
```

### Manual Testing
1. SSH Testing: Use Netmiko or direct SSH connection
2. SNMP Testing: Use `snmpwalk` or SNMP tools
3. Telnet Testing: Use telnet client
4. Netconf Testing: Use `netconf-console` or `ncclient`

### Test with Real Network Automation Tools
Test your device with popular automation tools:
- Netmiko: Python library for network device automation
- Ansible: Network automation platform
- NAPALM: Network automation library

## Submitting Changes

### 1. Create a Branch
```bash
git checkout -b feature/your-device-support
# or
git checkout -b fix/issue-description
```

### 2. Commit Your Changes
```bash
git add .
git commit -m "Add support for [device type]"
```

### 3. Push and Create Merge Request
```bash
git push origin feature/your-device-support
```

Then create a merge request on GitLab with:
- Clear description of changes
- Screenshots or test results
- Reference to any related issues

### 4. Merge Request Template
```markdown
## Description
Brief description of your changes

## Type of Change
- [ ] New device support
- [ ] Bug fix
- [ ] Documentation update
- [ ] Test improvement

## Testing
- [ ] Manual testing completed
- [ ] Automated tests pass
- [ ] Tested with [specific tools/libraries]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or documented)
```

## Code Style and Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small

### File Organization
- Device configs go in `configs/device_type/`
- Static templates in `templates/` subdirectory
- Dynamic scripts in `scripts/` subdirectory
- Tests in `tests/` directory

### Naming Conventions
- Device types: `vendor_os` (e.g., `cisco_ios`, `juniper_junos`)
- Command files: exact command name (e.g., `show version`)
- Version directories: `v6`, `v7`, etc.

## Documentation

### Device Documentation
When adding new devices, consider documenting:
- Device capabilities and limitations
- Supported commands
- Configuration examples
- Known issues or workarounds

### README Updates
Update relevant sections in `README.md` if you:
- Add new environment variables
- Change configuration options
- Add new features

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the project's mission

### Getting Help
- Check existing issues and discussions
- Ask questions in merge request comments
- Provide detailed information when reporting issues

### Recognition
Contributors will be recognized in:
- Project documentation
- Release notes
- Community acknowledgments

## Questions?

If you have questions about contributing:
1. Check existing issues and discussions
2. Create a new issue with the "question" label
3. Reach out to maintainers through merge request comments

Thank you for contributing to Mock'it! Your efforts help make network testing and development more accessible to everyone.
