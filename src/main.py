import os
import time
import logging
import asyncio
import asyncssh
from snmp_server import asyncsnmp_server
from src.start_server import start_server

def main():
    device_type = os.environ.get("DEVICE_TYPE", "a10")
    device_version = get_device_version(device_type, os.environ.get("DEVICE_VERSION", ""))
    prompt = get_prompt(device_type)
    options_ssh = {
        "debug"                 : str(os.environ.get("DEBUG_ENABLED", "false")).lower() == "true",
        "device_type"           : device_type,
        "device_version"        : device_version,
        "ssh_key"               : os.environ.get("SSH_KEY", "/ssh_key/rsa.key"),
        "username"              : os.environ.get("SSH_USERNAME", "root"),
        "password"              : os.environ.get("SSH_PASSWORD", ""),
        "delay"                 : int(os.environ.get("DEVICE_DELAY", 0)),
        "login_delay"           : int(os.environ.get("LOGIN_DELAY", 0)),
        "login_retry"           : int(os.environ.get("LOGIN_RETRY", 0)),
        "prompt"                : prompt,
        "response_format"       : get_response_format(device_type),
        "command_prompt_format" : get_command_format(device_type),
        "default_prompt_format" : get_prompt_format(device_type),
        "echo_format"           : get_echo_format(device_type),
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
        # loop.create_task(start_server(options_ssh))
        loop.run_until_complete(start_server(options_ssh))
        loop.run_forever()
    # if str(os.environ.get("SNMP_SERVER_ENABLED", "true")).lower() == "true":
    #     loop.create_task(asyncsnmp_server.start_server(options_snmp))
        
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

    if device_type == 'a10':
        return '>#'

    if device_type == 'adva_fsp150f2':
        return '-->'

    if device_type == 'adva_fsp150f3':
        return '-->'

    if device_type == 'apresia_aeos':
        return '>#'

    if device_type == 'aruba_osswitch':
        return '>#'

    if device_type == 'procurve':
        return '>#'

    if device_type == 'audiocode_shell':
        return '/>'

    if device_type == 'hp_comware':
        return '>'

    if device_type == 'huawei':
        return '>'
        
    if device_type == 'mikrotik_routeros':
        return ']>'


    return '#'

def get_response_format(device_type):
    format = os.environ.get("SSH_RESPONSE_FORMAT", "")
    if format:
        return format

    if device_type == 'cisco_wlc':
        return "<new_line><response><new_line>"

    if device_type == 'huawei':
        return "<new_line><response><new_line>"

    return "<response><new_line>"

def get_command_format(device_type):
    format = os.environ.get("SSH_COMMAND_PROMPT_FORMAT", "")
    if format:
        return format

    if device_type == 'hp_comware':
        return "<device_type>"

    if device_type == 'aruba_os':
        return "<device_type>"

    if device_type == 'cisco_wlc':
        return "<device_type>"

    if device_type == 'huawei':
        return "<device_type>"

    return "<device_type><prompt>"

def get_prompt_format(device_type):
    format = os.environ.get("SSH_DEFAULT_PROMPT_FORMAT", "")
    if format:
        return format

    return "<device_type><prompt>"

# Setting a value here disables asyncssh line_editor
def get_echo_format(device_type):
    format = os.environ.get("SSH_ECHO_FORMAT", "")
    if format:
        return format

    if device_type == 'cisco_wlc':
        return "<response>"

    if device_type == 'huawei':
        return "<response>"

    return ""

if __name__ == "__main__":
    LOGGER = logging.getLogger()
    logging.basicConfig(level=logging.DEBUG)
    main()
