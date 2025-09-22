import os
from collections import defaultdict
from functools import cache
from pathlib import Path

from netmiko.ssh_dispatcher import CLASS_MAPPER


override_file = Path(os.environ.get("ENV_FILE", "/etc/mockit/env"))
bool2str = dict(zip([False, True], ['false', 'true']))


def process_config_line(line: str) -> tuple[str, str] | None:
    valid = line and line[0] != '#' and '=' in line
    result = line.strip().split('=', 1) if valid else None
    return result


def extract_options(content) -> dict[str, str]:
    lines = content.splitlines()
    result = dict(filter(None, map(process_config_line, lines)))
    return result


@cache
def get_overridden_options():
    result = {}
    if override_file.exists() and override_file.is_file():
        result = extract_options(override_file.read_text())
    return result


def get_opt(name, default: str | None = None, as_bool: bool = False):
    override_options = get_overridden_options()
    result = override_options.get(name, os.environ.get(name) or default)
    if as_bool:
        result = result and result.lower() == "true"
    return result


def get_normalized_device_type(device_type):
    result = (device_type.removesuffix("_ssh").removesuffix("_telnet")
              if device_type else device_type)
    return result


def get_options():
    enable_reload = get_opt("ENABLE_RELOAD", as_bool=True)
    device_type = get_opt("DEVICE_TYPE")
    device_version = get_opt("DEVICE_VERSION", "")
    debug_enabled = get_opt('DEBUG_ENABLED', as_bool=True)
    normalized = get_normalized_device_type(device_type)
    enable_ssh = bool2str[bool(CLASS_MAPPER.get(f"{normalized}_ssh"))]
    enable_telnet = bool2str[bool(CLASS_MAPPER.get(f"{normalized}_telnet"))]

    options = {
        'ENABLE_RELOAD': enable_reload,
        'UDP_RELOAD_PORT': int(get_opt("UDP_RELOAD_PORT", 0)),
        'DEVICE_TYPE': device_type,
        'DEVICE_VERSION': device_version,
        'DEBUG_ENABLED': debug_enabled,
        'SSH_SERVER_ENABLED': get_opt("SSH_SERVER_ENABLED", enable_ssh, as_bool=True),
        'SNMP_SERVER_ENABLED': get_opt("SNMP_SERVER_ENABLED", "true", as_bool=True),
        'NETCONF_SERVER_ENABLED': get_opt("NETCONF_SERVER_ENABLED", "true", as_bool=True),
        'TELNET_SERVER_ENABLED': get_opt("TELNET_SERVER_ENABLED", enable_telnet, as_bool=True),
        'ssh': {
            "debug": debug_enabled,
            "device_type": device_type,
            "ssh_key": get_opt("SSH_KEY", "/ssh_key/rsa.key"),
            "username": get_opt("SSH_USERNAME", "root"),
            "password": get_opt("SSH_PASSWORD", ""),
            "delay": int(get_opt("DEVICE_DELAY", 0)),
            "login_delay": int(get_opt("LOGIN_DELAY", 0)),
            "login_retry": int(get_opt("LOGIN_RETRY", 0)),
            "openai_support": get_opt("OPENAI_SUPPORT", as_bool=True),
            "openai_apikey": get_opt("OPENAI_APIKEY", ""),
            "device_version": device_version,
            "authkey_enabled": get_opt("AUTHKEY_ENABLED", "false", as_bool=True),
            "authkey_path": os.environ.get("AUTHKEY_PATH", ""),
            "enable_mode": get_opt("ENABLE_MODE", "false", as_bool=True),
            "enable_security": get_opt("ENABLE_SECURITY", "false", as_bool=True),
            "port": int(get_opt("SSH_PORT", '22')),
        },
        'snmp': {
            "debug": debug_enabled,
            "device_type": device_type,
            "device_version": device_version,
            "snmpv2_enabled": get_opt("SNMP_V2_ENABLED", as_bool=True),
            "snmpv2_name": get_opt("SNMP_V2_COMMUNITY", ""),
            "snmpv3_enabled": get_opt("SNMP_V3_ENABLED", as_bool=True),
            "snmpv3_username": get_opt("SNMP_V3_USERNAME", "usr-none-none"),
            "snmpv3_authtype": get_opt("SNMP_V3_AUTH_TYPE", "none"),
            "snmpv3_authkey": get_opt("SNMP_V3_AUTH_KEY", ""),
            "snmpv3_privtype": get_opt("SNMP_V3_PRIV_TYPE", "none"),
            "snmpv3_privkey": get_opt("SNMP_V3_PRIV_KEY", ""),
            "openai_support": get_opt("OPENAI_SUPPORT", as_bool=True),
            "openai_apikey": get_opt("OPENAI_APIKEY", ""),
        },
        'netconf': {
            "device_type": device_type,
            "username": get_opt("NETCONF_USERNAME", "test"),
            "password": get_opt("NETCONF_PASSWORD", "test"),
            "authorized_key": get_opt("NETCONF_KEY", ""),
        },
        'telnet': {
            "device_type": device_type,
            "username": get_opt("TELNET_USERNAME", "root"),
            "password": get_opt("TELNET_PASSWORD", ""),
            "delay": float(get_opt("DEVICE_DELAY", '0.025')),
            "device_version": device_version
        },
    }
    return options
