import os
import socket
import io
import re
from contextlib import suppress
from functools import cache

from netmiko import ConnectHandler
from netmiko.alaxala import alaxala_ax36s
from netmiko.ssh_dispatcher import CLASS_MAPPER_BASE

import pytest


CHANNELS = ['telnet', 'ssh']

SSH_PLATFORMS_SUPPORTED = [
    "a10",
    "accedian",
    "adtran_os",
    "alcatel_aos",
    "alcatel_sros",
    "allied_telesis_awplus",
    "apresia_aeos",
    "arista_eos",
    "arris_cer",
    "aruba_os",
    "aruba_osswitch",
    "aruba_procurve",
    # "audiocode_66",
    # "audiocode_72",
    "avaya_ers",
    "avaya_vsp",
    "broadcom_icos",
    "brocade_fastiron",
    "brocade_fos",
    "brocade_netiron",
    "brocade_nos",
    "brocade_vdx",
    "brocade_vyos",
    "calix_b6",
    "casa_cmts",
    "cdot_cros",
    "centec_os",
    "checkpoint_gaia",
    "ciena_saos",
    "cisco_asa",
    "cisco_ftd",
    "cisco_ios",
    "cisco_nxos",
    "cisco_s200",
    "cisco_s300",
    "cisco_viptela",
    "cisco_wlc",
    "cisco_xe",
    "cisco_xr",
    "cloudgenix_ion",
    "coriant",
    "dell_dnos9",
    "dell_force10",
    "dell_isilon",
    "dell_os10",
    "dell_os6",
    "dell_os9",
    "dell_powerconnect",
    "dell_sonic",
    "digi_transport",
    "dlink_ds",
    "eltex",
    "eltex_esr",
    "endace",
    "enterasys",
    "ericsson_ipos",
    "ericsson_mltn63",
    "ericsson_mltn66",
    "extreme",
    "extreme_ers",
    "extreme_exos",
    "extreme_netiron",
    "extreme_nos",
    "extreme_slx",
    "extreme_tierra",
    "extreme_vdx",
    "extreme_vsp",
    "extreme_wing",
    "f5_linux",
    "f5_ltm",
    "f5_tmsh",
    "fiberstore_fsos",
    "flexvnf",
    "fortinet",
    "generic",
    "generic_termserver",
    "hp_comware",
    "hp_procurve",
    "huawei",
    # "huawei_olt",
    # "huawei_smartax",
    "huawei_vrpv8",
    "ipinfusion_ocnos",
    "juniper_junos",
    "juniper_screenos",
    "keymile",
    "keymile_nos",
    "linux",
    "mellanox",
    "mellanox_mlnxos",
    "mikrotik_routeros",
    "mikrotik_switchos",
    "mrv_lx",
    "mrv_optiswitch",
    "netapp_cdot",
    "netgear_prosafe",
    "netscaler",
    "nokia_srl",
    "nokia_sros",
    "oneaccess_oneos",
    "ovs_linux",
    "paloalto_panos",
    "quanta_mesh",
    "rad_etx",
    "raisecom_roap",
    "ruckus_fastiron",
    "ruijie_os",
    "sixwind_os",
    "sophos_sfos",
    "supermicro_smis",
    "tplink_jetstream",
    "ubiquiti_edgerouter",
    "ubiquiti_edgeswitch",
    "ubiquiti_unifiswitch",
    "vyatta_vyos",
    "vyos",
    "watchguard_fireware",
    "yamaha",
    "zte_zxros",
    "zyxel_os",

    # "adva_fsp150f2",
    # "adva_fsp150f3",
    "alaxala_ax26s",
    "alaxala_ax36s",
    "arris_cer",
    "casa_cmts",
    "cisco_apic",
    "cisco_s200",
    "digi_transport",
    "ericsson_mltn63",
    "ericsson_mltn66",
    "fiberstore_fsos",
    "garderos_grs",
    "hillstone_stoneos",
    "huawei_vrp",
    "juniper",
    "ubiquiti_edge",
    "vertiv_mph",
]


TELNET_PLATFORMS_SUPPORTED = [
    # "adtran_os",
    # "apresia_aeos",
    # "arista_eos",
    # "aruba_procurve",
    # # "audiocode_66",
    # # "audiocode_72",
    # "audiocode_shell",
    # "brocade_fastiron",
    # "brocade_netiron",
    # "calix_b6",
    # "centec_os",
    # "ciena_saos",
    # "cisco_ios",
    # "cisco_s200",
    # "cisco_s300",
    # "cisco_xr",
    # "dell_dnos6",
    # "dell_powerconnect",
    # "dlink_ds",
    # "extreme",
    # "extreme_exos",
    # "extreme_netiron",
    # "generic",
    # "hp_comware",
    # "hp_procurve",
    # "huawei",
    # # "huawei_olt",
    # "ipinfusion_ocnos",
    # "juniper_junos",
    # "maipu",
    # "nokia_sros",
    # "oneaccess_oneos",
    # "rad_etx",
    # "raisecom",
    # "ruckus_fastiron",
    # "ruijie_os",
    # "supermicro_smis",
    # "teldat_cit",
    # "tplink_jetstream",
    # "yamaha",
    # "zte_zxros",
]


DEVICE_VERSIONS = {
    "mikrotik_routeros": ["v6", "v7"]
}

# Devices that should have enable mode enabled during testing
DEVICES_WITH_ENABLE_MODE = {
    "apresia_aeos": True,
    "huawei_olt": True,
    "huawei_smartax": True
    # Add more devices as needed
}

# Enable secrets for devices (optional)
DEVICE_ENABLE_SECRETS = {
    # Add more devices as needed
}

# modify here the set of platforms for reduced set when testing
# SSH_PLATFORMS_SUPPORTED = []
# TELNET_PLATFORMS_SUPPORTED = []


def coerce_int(value):
    if value is not None:
        with suppress(ValueError):
            value = int(value)
    return value


# set up variables for dev:
#   if not specified, should match the once in docker-compose_ssh_telnet.yml
mocked_device = os.environ.get('MOCKIT_HOST', 'mocked-device')
ssh_port = coerce_int(os.environ.get('MOCKIT_SSH_PORT', 22))
telnet_port = coerce_int(os.environ.get('MOCKIT_TELNET_PORT', 23))
mocked_udp_restart_port = coerce_int(os.environ.get('MOCKIT_UDP_RESTART_PORT', 9999))


@cache
def get_parameters():
    """Generate test parameters for all service/device_type/version combinations"""
    params = []
    all_platforms = set(SSH_PLATFORMS_SUPPORTED + TELNET_PLATFORMS_SUPPORTED)
    for device_type in sorted(all_platforms):
        versions = DEVICE_VERSIONS.get(device_type, [None])
        for version in versions:
            reconfigure = True
            start_telnet = device_type in TELNET_PLATFORMS_SUPPORTED
            ch_ssh = [False] if device_type in SSH_PLATFORMS_SUPPORTED else []
            ch_telnet = [True] if start_telnet else []
            channels = ch_ssh + ch_telnet
            for channel in channels:
                params.append((device_type, version, channel, reconfigure, start_telnet))
                reconfigure = False
    return params


def get_ids_from_params(params):
    ids = []
    for device_type, version, channel, reconfigure, start_telnet in params:
        ch = 'telnet' if channel else 'ssh'
        if reconfigure:
            reconf = '-reconfigure'
            if start_telnet:
                reconf += '-with_telnet'
        else:
            reconf = ''
        device_type_version = '_'.join(filter(None, [device_type, version]))
        ids.append(f"{device_type_version}-{ch}{reconf}")
    return ids




def reconfigure_device(device_type: str, version: str | None, enable_telnet: bool, enable_mode: bool = False, enable_secret: str = ""):
    message = (f"DEVICE_TYPE={device_type}\n"
               f"DEVICE_VERSION={version or ''}\n"
               f"TELNET_SERVER_ENABLED={bool(enable_telnet)}\n"
               f"ENABLE_MODE={str(enable_mode).lower()}\n"
               f"ENABLE_SECRET={enable_secret}\n")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('', 0))
        sock.sendto(message.encode(), (mocked_device, mocked_udp_restart_port))
        sock.settimeout(20)
        sock.recvfrom(1024)
    finally:
        sock.close()

@pytest.mark.parametrize(
    "device_type, version, telnet, reconfigure, start_telnet",
    get_parameters(),
    ids=get_ids_from_params(get_parameters()),
)
def test_mock_device(device_type: str, version: str, telnet: bool, reconfigure: bool, start_telnet: bool):
    if reconfigure:
        # Check if this device should have enable mode enabled
        enable_mode = DEVICES_WITH_ENABLE_MODE.get(device_type, False)
        enable_secret = DEVICE_ENABLE_SECRETS.get(device_type, "")
        reconfigure_device(device_type, version, start_telnet, enable_mode, enable_secret)

    
    platform = f"{device_type}_telnet" if telnet else device_type
    session_buffer = io.BytesIO()
    parameters = {
        "device_type": platform,
        "host": mocked_device,
        "port": telnet_port if telnet else ssh_port,
        "username": "root",
        "password": "test",
        "verbose": True,
        "fast_cli": False,
        "conn_timeout": 10,
        "session_log": session_buffer
    }
    try:
        with ConnectHandler(**parameters) as net_connect:
            assert net_connect.send_command('echo test') == "test", f'Test failed on {parameters} - \n' + get_session_log(session_buffer)
    except:
        print(get_session_log(session_buffer))
        raise
    finally:
        session_buffer.close()


def test_enable_mode_functionality():
    """Test enable mode functionality for devices that support it"""
    test_devices = ["cisco_ios", "arista_eos", "juniper_junos"]
    
    for device_type in test_devices:
        # Configure device with enable mode
        enable_secret = DEVICE_ENABLE_SECRETS.get(device_type, "test123")
        reconfigure_device(device_type, None, False, True, enable_secret)
        
        session_buffer = io.BytesIO()
        # Test SSH connection and enable command
        parameters = {
            "device_type": device_type,
            "host": mocked_device,
            "port": ssh_port,
            "username": "root",
            "password": "test",
            "secret": enable_secret,
            "verbose": True,
            "fast_cli": False,
            "conn_timeout": 10,
            "session_log": session_buffer
        }
        try:
            with ConnectHandler(**parameters) as net_connect:
                # Test basic command first
                result = net_connect.send_command('echo test')
                assert result == "test", f'Basic command failed for {parameters} - \n' + get_session_log(session_buffer)
                
                # Test enable command (this should prompt for password)
                # Note: This test might need adjustment based on how netmiko handles enable mode
                try:
                    net_connect.enable()
                    # If enable succeeds, test privileged command
                    result = net_connect.send_command('show version')
                    assert result is not None, f'Enable mode failed for {parameters} - \n' + get_session_log(session_buffer)
                except:
                    print(get_session_log(session_buffer))
                    raise
        finally:
            session_buffer.close()

def get_session_log(buffer):
    buffer.seek(0)
    log_text = buffer.read().decode("utf-8", errors="ignore")
    return re.sub(r"\n\s*\n", "\n", log_text)
