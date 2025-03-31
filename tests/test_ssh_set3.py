from netmiko import ConnectHandler, platforms  
import pytest

def run_command(host, device_type, command, username="root", password="test"):
    parameters = { 
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
        "verbose": True,
        "fast_cli": False
    }

    with ConnectHandler(**parameters) as net_connect:
        return net_connect.send_command(command)

@pytest.mark.test_set3
def test_hp_comware():
    assert run_command("devices_hp_comware", "hp_comware", "echo test") == "test"

@pytest.mark.test_set3
def test_hp_procurve():
    assert run_command("devices_hp_procurve", "hp_procurve", "echo test") == "test"

@pytest.mark.test_set3
def test_huawei():
    assert run_command("devices_huawei", "huawei", "echo test") == "test"

@pytest.mark.test_set3
def test_huawei_olt():
    assert run_command("devices_huawei_olt", "huawei_olt", "echo test") == "test"

@pytest.mark.test_set3
def test_huawei_smartax():
    assert run_command("devices_huawei_smartax", "huawei_smartax", "echo test") == "test"

@pytest.mark.test_set3
def test_huawei_vrpv8():
    assert run_command("devices_huawei_vrpv8", "huawei_vrpv8", "echo test") == "test"

@pytest.mark.test_set3
def test_ipinfusion_ocnos():
    assert run_command("devices_ipinfusion_ocnos", "ipinfusion_ocnos", "echo test") == "test"

@pytest.mark.test_set3
def test_juniper_junos():
    assert run_command("devices_juniper_junos", "juniper_junos", "echo test") == "test"

@pytest.mark.test_set3
def test_juniper_screenos():
    assert run_command("devices_juniper_screenos", "juniper_screenos", "echo test") == "test"

@pytest.mark.test_set3
def test_keymile():
    assert run_command("devices_keymile", "keymile", "echo test") == "test"

@pytest.mark.test_set3
def test_keymile_nos():
    assert run_command("devices_keymile_nos", "keymile_nos", "echo test") == "test"

@pytest.mark.test_set3
def test_linux():
    assert run_command("devices_linux", "linux", "echo test") == "test"

@pytest.mark.test_set3
def test_mellanox():
    assert run_command("devices_mellanox", "mellanox", "echo test") == "test"

@pytest.mark.test_set3
def test_mellanox_mlnxos():
    assert run_command("devices_mellanox_mlnxos", "mellanox_mlnxos", "echo test") == "test"

@pytest.mark.test_set3
def test_mikrotik_routeros_v6():
    assert run_command("devices_mikrotik_routeros_v6", "mikrotik_routeros", "echo test") == "test"

@pytest.mark.test_set3
def test_mikrotik_routeros_v7():
    assert run_command("devices_mikrotik_routeros_v7", "mikrotik_routeros", "echo test") == "test"

@pytest.mark.test_set3
def test_mikrotik_switchos():
    assert run_command("devices_mikrotik_switchos", "mikrotik_switchos", "echo test") == "test"

@pytest.mark.test_set3
def test_mrv_lx():
    assert run_command("devices_mrv_lx", "mrv_lx", "echo test") == "test"

@pytest.mark.test_set3
def test_mrv_optiswitch():
    assert run_command("devices_mrv_optiswitch", "mrv_optiswitch", "echo test") == "test"

@pytest.mark.test_set3
def test_netapp_cdot():
    assert run_command("devices_netapp_cdot", "netapp_cdot", "echo test") == "test"

@pytest.mark.test_set3
def test_netgear_prosafe():
    assert run_command("devices_netgear_prosafe", "netgear_prosafe", "echo test") == "test"

@pytest.mark.test_set3
def test_netscaler():
    assert run_command("devices_netscaler", "netscaler", "echo test") == "test"

@pytest.mark.test_set3
def test_nokia_srl():
    assert run_command("devices_nokia_srl", "nokia_srl", "echo test") == "test"

@pytest.mark.test_set3
def test_nokia_sros():
    assert run_command("devices_nokia_sros", "nokia_sros", "echo test") == "test"

@pytest.mark.test_set3
def test_oneaccess_oneos():
    assert run_command("devices_oneaccess_oneos", "oneaccess_oneos", "echo test") == "test"

@pytest.mark.test_set3
def test_ovs_linux():
    assert run_command("devices_ovs_linux", "ovs_linux", "echo test") == "test"

@pytest.mark.test_set3
def test_paloalto_panos():
    assert run_command("devices_paloalto_panos", "paloalto_panos", "echo test") == "test"

@pytest.mark.test_set3
def test_quanta_mesh():
    assert run_command("devices_quanta_mesh", "quanta_mesh", "echo test") == "test"

@pytest.mark.test_set3
def test_rad_etx():
    assert run_command("devices_rad_etx", "rad_etx", "echo test") == "test"

@pytest.mark.test_set3
def test_raisecom_roap():
    assert run_command("devices_raisecom_roap", "raisecom_roap", "echo test") == "test"

@pytest.mark.test_set3
def test_ruckus_fastiron():
    assert run_command("devices_ruckus_fastiron", "ruckus_fastiron", "echo test") == "test"

@pytest.mark.test_set3
def test_ruijie_os():
    assert run_command("devices_ruijie_os", "ruijie_os", "echo test") == "test"

@pytest.mark.test_set3
def test_sixwind_os():
    assert run_command("devices_sixwind_os", "sixwind_os", "echo test") == "test"

@pytest.mark.test_set3
def test_sophos_sfos():
    assert run_command("devices_sophos_sfos", "sophos_sfos", "echo test") == "test"

@pytest.mark.test_set3
def test_supermicro_smis():
    assert run_command("devices_supermicro_smis", "supermicro_smis", "echo test") == "test"

@pytest.mark.test_set3
def test_tplink_jetstream():
    assert run_command("devices_tplink_jetstream", "tplink_jetstream", "echo test") == "test"

@pytest.mark.test_set3
def test_ubiquiti_edgerouter():
    assert run_command("devices_ubiquiti_edgerouter", "ubiquiti_edgerouter", "echo test") == "test"

@pytest.mark.test_set3
def test_ubiquiti_edgeswitch():
    assert run_command("devices_ubiquiti_edgeswitch", "ubiquiti_edgeswitch", "echo test") == "test"

@pytest.mark.test_set3
def test_ubiquiti_unifiswitch():
    assert run_command("devices_ubiquiti_unifiswitch", "ubiquiti_unifiswitch", "echo test") == "test"

@pytest.mark.test_set3
def test_vyatta_vyos():
    assert run_command("devices_vyatta_vyos", "vyatta_vyos", "echo test") == "test"

@pytest.mark.test_set3
def test_vyos():
    assert run_command("devices_vyos", "vyos", "echo test") == "test"

@pytest.mark.test_set3
def test_watchguard_fireware():
    assert run_command("devices_watchguard_fireware", "watchguard_fireware", "echo test") == "test"

@pytest.mark.test_set3
def test_yamaha():
    assert run_command("devices_yamaha", "yamaha", "echo test") == "test"

@pytest.mark.test_set3
def test_zte_zxros():
    assert run_command("devices_zte_zxros", "zte_zxros", "echo test") == "test"

@pytest.mark.test_set3
def test_zyxel_os():
    assert run_command("devices_zyxel_os", "zyxel_os", "echo test") == "test"
