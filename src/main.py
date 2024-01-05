import os
import time
import logging
import asyncio
import asyncssh
from ssh_server import asyncssh_server
from snmp_server import asyncsnmp_server

def main():
    device_type = os.environ.get("DEVICE_TYPE", "cisco_ios")
    device_version = get_device_version(device_type, os.environ.get("DEVICE_VERSION", ""))
    prompt = get_prompt(device_type)
    options_ssh = {
        "debug"         : str(os.environ.get("DEBUG_ENABLED", "false")).lower() == "true",
        "device_type"   : device_type,
        "device_version": device_version,

        "ssh_key"       : os.environ.get("SSH_KEY", "/ssh_key/rsa.key"),
        "username"      : os.environ.get("SSH_USERNAME", "root"),
        "password"      : os.environ.get("SSH_PASSWORD", ""),
        "prompt"        : prompt,
        "prompt_command": get_command_prompt(device_type, prompt),
    }
    options_snmp = {
        "debug"             : str(os.environ.get("DEBUG_ENABLED", "false")).lower() == "true",
        "device_type"       : device_type,
        "device_version"    : device_version,

        "snmpv2_enabled"    : str(os.environ.get("SNMP_V2_ENABLED", "true")).lower() == "true",
        "snmpv2_name"       : os.environ.get("SNMP_V2_NAME", ""),

        "snmpv3_enabled"    : str(os.environ.get("SNMP_V3_ENABLED", "false")).lower() == "true",
        "snmpv3_username"   : os.environ.get("SNMP_V3_USERNAME", "usr-none-none"),
        "snmpv3_authtype"   : os.environ.get("SNMP_V3_AUTH_TYPE", "none"),
        "snmpv3_authkey"    : os.environ.get("SNMP_V3_AUTH_KEY", ""),
        "snmpv3_privtype"   : os.environ.get("SNMP_V3_PRIV_TYPE", "none"),
        "snmpv3_privkey"    : os.environ.get("SNMP_V3_PRIV_KEY", ""),
    }
    
    loop = asyncio.get_event_loop()
    if str(os.environ.get("SSH_SERVER_ENABLED", "true")).lower() == "true":
        loop.create_task(asyncssh_server.start_server(options_ssh))
    if str(os.environ.get("SNMP_SERVER_ENABLED", "true")).lower() == "true":
        loop.create_task(asyncsnmp_server.start_server(options_snmp))
        
    if len(asyncio.all_tasks(loop)) == 0:
        raise Exception("No tasks were started")
    loop.run_forever()

def get_device_version(device_type, version):
    if version:
        return version

    if device_type == "mikrotik_routeros":
        return "v7"

    return version

def get_prompt(device_type):
    prompt = os.environ.get("SSH_PROMPT", "")
    if prompt:
        return prompt

    if device_type == 'hp_comware':
        return '>'

    if device_type == 'huawei':
        return '>'
        
    if device_type == 'mikrotik_routeros':
        return ']>'


    return '#'

def get_command_prompt(device_type, default_prompt):
    prompt = os.environ.get("SSH_PROMPT_COMMAND", "")
    if prompt:
        return prompt

    if device_type == 'hp_comware':
        return ''

    if device_type == 'aruba_os':
        return ''

    return default_prompt

if __name__ == "__main__":
    LOGGER = logging.getLogger()
    logging.basicConfig(level=logging.DEBUG)
    main()
