import os
import time
import logging
import asyncio
import asyncssh
from snmp_server import asyncsnmp_server
from src.start_ssh import start_ssh
from src.start_netconf import start_netconf

def main():
    # Fetch device type from environment variable
    device_type = os.environ.get("DEVICE_TYPE")
    
    if not device_type:
        print("Device type is incorrect!")
        return
    # Fetch device version or determine based on device type
    device_version = os.environ.get("DEVICE_VERSION", "")
    
    # SSH configuration options from environment variables
    options_ssh = {
        "debug": str(os.environ.get("DEBUG_ENABLED", "false")).lower() == "true",
        "device_type": device_type,
        "ssh_key": os.environ.get("SSH_KEY", "/ssh_key/rsa.key"),
        "username": os.environ.get("SSH_USERNAME", "root"),
        "password": os.environ.get("SSH_PASSWORD", ""),
        "delay": int(os.environ.get("DEVICE_DELAY", 0)),
        "login_delay": int(os.environ.get("LOGIN_DELAY", 0)),
        "login_retry": int(os.environ.get("LOGIN_RETRY", 0)),
        "openai_support": str(os.environ.get("OPENAI_SUPPORT", "false")).lower() == "true",
        "openai_apikey": os.environ.get("OPENAI_APIKEY", ""),
        "device_version": device_version
    }
    
    # SNMP configuration options from environment variables
    options_snmp = {
        "debug": str(os.environ.get("DEBUG_ENABLED", "false")).lower() == "true",
        "device_type": device_type,
        "device_version": device_version,
        "snmpv2_enabled": str(os.environ.get("SNMP_V2_ENABLED", "true")).lower() == "true",
        "snmpv2_name": os.environ.get("SNMP_V2_COMMUNITY", ""),
        "snmpv3_enabled": str(os.environ.get("SNMP_V3_ENABLED", "false")).lower() == "true",
        "snmpv3_username": os.environ.get("SNMP_V3_USERNAME", "usr-none-none"),
        "snmpv3_authtype": os.environ.get("SNMP_V3_AUTH_TYPE", "none"),
        "snmpv3_authkey": os.environ.get("SNMP_V3_AUTH_KEY", ""),
        "snmpv3_privtype": os.environ.get("SNMP_V3_PRIV_TYPE", "none"),
        "snmpv3_privkey": os.environ.get("SNMP_V3_PRIV_KEY", ""),
        "openai_support": str(os.environ.get("OPENAI_SUPPORT", "false")).lower() == "true",
        "openai_apikey": os.environ.get("OPENAI_APIKEY", ""),
    }

    options_netconf = {
        "device_type": device_type,
        "username": os.environ.get("NETCONF_USERNAME", "test"),
        "password": os.environ.get("NETCONF_PASSWORD", "test"),
        "authorized_key": os.environ.get("NETCONF_KEY", ""),
    }
    
    
    loop = asyncio.get_event_loop()
    if str(os.environ.get("SSH_SERVER_ENABLED", "true")).lower() == "true":
        loop.create_task(start_ssh(options_ssh))
    if str(os.environ.get("SNMP_SERVER_ENABLED", "true")).lower() == "true":
        loop.create_task(asyncsnmp_server.start_server(options_snmp))
    if str(os.environ.get("NETCONF_SERVER_ENABLED", "true")).lower() == "true":
        loop.create_task(start_netconf(options_netconf))
        
    if len(asyncio.all_tasks(loop)) == 0:
        raise Exception("No tasks were started")
    loop.run_forever()

if __name__ == "__main__":
    # Setup logging
    LOGGER = logging.getLogger()
    logging.basicConfig(level=logging.DEBUG)
    
    # Start main function
    main()
