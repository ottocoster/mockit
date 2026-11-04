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

    # API driver detection: a driver is "API-only" when it ships api/routes.json
    # but is not a known Netmiko platform. For those, the CLI/SNMP/NETCONF servers
    # default off and only the API server runs.
    api_dir = Path(f"configs/{normalized}")
    if device_version:
        api_dir = api_dir / device_version
    api_available = (api_dir / "api" / "routes.json").exists()
    is_netmiko = bool(
        CLASS_MAPPER.get(normalized)
        or CLASS_MAPPER.get(f"{normalized}_ssh")
        or CLASS_MAPPER.get(f"{normalized}_telnet")
    )
    api_only = api_available and not is_netmiko
    enable_api = bool2str[api_available]
    legacy_default = bool2str[not api_only]

    options = {
        'ENABLE_RELOAD': enable_reload,
        'UDP_RELOAD_PORT': int(get_opt("UDP_RELOAD_PORT", 0)),
        'DEVICE_TYPE': device_type,
        'DEVICE_VERSION': device_version,
        'DEBUG_ENABLED': debug_enabled,
        'SSH_SERVER_ENABLED': get_opt("SSH_SERVER_ENABLED", enable_ssh, as_bool=True),
        'SNMP_SERVER_ENABLED': get_opt("SNMP_SERVER_ENABLED", legacy_default, as_bool=True),
        'NETCONF_SERVER_ENABLED': get_opt("NETCONF_SERVER_ENABLED", legacy_default, as_bool=True),
        'TELNET_SERVER_ENABLED': get_opt("TELNET_SERVER_ENABLED", enable_telnet, as_bool=True),
        'API_SERVER_ENABLED': get_opt("API_SERVER_ENABLED", enable_api, as_bool=True),
        'ssh': {
            "debug": debug_enabled,
            "device_type": device_type,
            "ssh_key": get_opt("SSH_KEY", "/ssh_key/rsa.key"),
            "username": get_opt("SSH_USERNAME", "root"),
            "password": get_opt("SSH_PASSWORD", ""),
            "kex_algorithms": get_opt("SSH_KEX_ALGORITHMS", "diffie-hellman-group1-sha1,diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1,diffie-hellman-group-exchange-sha256,curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521"),
            "ciphers": get_opt("SSH_CIPHERS", ""),
            "delay": int(get_opt("DEVICE_DELAY", 0)),
            "login_delay": int(get_opt("LOGIN_DELAY", 0)),
            "login_retry": int(get_opt("LOGIN_RETRY", 0)),
            "ai_support": get_opt("AI_SUPPORT", as_bool=True),
            "ai_apikey": get_opt("AI_APIKEY", ""),
            "ai_url": get_opt("AI_URL", ""),
            "ai_model": get_opt("AI_MODEL", "gpt-5.5"),
            "ai_store_responses": get_opt("AI_STORE_RESPONSES", as_bool=True),
            "ai_terminal_output": get_opt("AI_TERMINAL_OUTPUT", None),
            "ai_terminal_prompt": get_opt("AI_TERMINAL_PROMPT", None),
            "device_version": device_version,
            "authkey_enabled": get_opt("AUTHKEY_ENABLED", "false", as_bool=True),
            "authkey_path": os.environ.get("AUTHKEY_PATH", ""),
            "enable_mode": get_opt("ENABLE_MODE", "false", as_bool=True),
            "enable_secret": get_opt("ENABLE_SECRET", ""),
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
            "ai_support": get_opt("AI_SUPPORT", as_bool=True),
            "ai_apikey": get_opt("AI_APIKEY", ""),
            "ai_url": get_opt("AI_URL", ""),
            "ai_model": get_opt("AI_MODEL", "gpt-5.5"),
            "ai_store_responses": get_opt("AI_STORE_RESPONSES", as_bool=True),
            "ai_snmp_output": get_opt("AI_SNMP_OUTPUT", None),
            "ai_snmp_prompt": get_opt("AI_SNMP_PROMPT", None),
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
        'api': {
            "debug": debug_enabled,
            "device_type": device_type,
            "device_version": device_version,
            "port": int(get_opt("API_PORT", '443')),
            "tls": get_opt("API_TLS", "false", as_bool=True),
            "cert": get_opt("API_CERT", "/api_cert/cert.pem"),
            "key": get_opt("API_TLS_KEY", "/api_cert/key.pem"),
            "auth_type": get_opt("API_AUTH_TYPE", "none"),
            "token": get_opt("API_TOKEN", ""),
            "api_key": get_opt("API_KEY", ""),
            "api_key_header": get_opt("API_KEY_HEADER", "X-API-KEY"),
            "oauth_client_id": get_opt("API_OAUTH_CLIENT_ID", ""),
            "oauth_client_secret": get_opt("API_OAUTH_CLIENT_SECRET", ""),
            "oauth_access_token": get_opt("API_OAUTH_ACCESS_TOKEN", "mockit-access-token"),
            "oauth_auth_code": get_opt("API_OAUTH_AUTH_CODE", "mockit-auth-code"),
            "oauth_refresh_token": get_opt("API_OAUTH_REFRESH_TOKEN", "mockit-refresh-token"),
        },
    }
    return options
