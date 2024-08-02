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

@pytest.mark.test_set2
def test_dell_dnos9():
    assert run_command("devices-dell_dnos9", "dell_dnos9", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_force10():
    assert run_command("devices-dell_force10", "dell_force10", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_isilon():
    assert run_command("devices-dell_isilon", "dell_isilon", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_os6():
    assert run_command("devices-dell_os6", "dell_os6", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_os9():
    assert run_command("devices-dell_os9", "dell_os9", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_os10():
    assert run_command("devices-dell_os10", "dell_os10", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_powerconnect():
    assert run_command("devices-dell_powerconnect", "dell_powerconnect", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_sonic():
    assert run_command("devices-dell_sonic", "dell_sonic", "echo test") == "test"

@pytest.mark.test_set2
def test_digi_transport():
    assert run_command("devices-digi_transport", "digi_transport", "echo test") == "test"

@pytest.mark.test_set2
def test_dlink_ds():
    assert run_command("devices-dlink_ds", "dlink_ds", "echo test") == "test"

@pytest.mark.test_set2
def test_eltex():
    assert run_command("devices-eltex", "eltex", "echo test") == "test"

@pytest.mark.test_set2
def test_eltex_esr():
    assert run_command("devices-eltex_esr", "eltex_esr", "echo test") == "test"

@pytest.mark.test_set2
def test_endace():
    assert run_command("devices-endace", "endace", "echo test") == "test"

@pytest.mark.test_set2
def test_enterasys():
    assert run_command("devices-enterasys", "enterasys", "echo test") == "test"

@pytest.mark.test_set2
def test_ericsson_ipos():
    assert run_command("devices-ericsson_ipos", "ericsson_ipos", "echo test") == "test"

@pytest.mark.test_set2
def test_ericsson_mltn63():
    assert run_command("devices-ericsson_mltn63", "ericsson_mltn63", "echo test") == "test"

@pytest.mark.test_set2
def test_ericsson_mltn66():
    assert run_command("devices-ericsson_mltn66", "ericsson_mltn66", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme():
    assert run_command("devices-extreme", "extreme", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_ers():
    assert run_command("devices-extreme_ers", "extreme_ers", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_exos():
    assert run_command("devices-extreme_exos", "extreme_exos", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_netiron():
    assert run_command("devices-extreme_netiron", "extreme_netiron", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_nos():
    assert run_command("devices-extreme_nos", "extreme_nos", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_slx():
    assert run_command("devices-extreme_slx", "extreme_slx", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_tierra():
    assert run_command("devices-extreme_tierra", "extreme_tierra", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_vdx():
    assert run_command("devices-extreme_vdx", "extreme_vdx", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_vsp():
    assert run_command("devices-extreme_vsp", "extreme_vsp", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_wing():
    assert run_command("devices-extreme_wing", "extreme_wing", "echo test") == "test"

@pytest.mark.test_set2
def test_f5_linux():
    assert run_command("devices-f5_linux", "f5_linux", "echo test") == "test"

@pytest.mark.test_set2
def test_f5_ltm():
    assert run_command("devices-f5_ltm", "f5_ltm", "echo test") == "test"

@pytest.mark.test_set2
def test_f5_tmsh():
    assert run_command("devices-f5_tmsh", "f5_tmsh", "echo test") == "test"

@pytest.mark.test_set2
def test_fiberstore_fsos():
    assert run_command("devices-fiberstore_fsos", "fiberstore_fsos", "echo test") == "test"

@pytest.mark.test_set2
def test_flexvnf():
    assert run_command("devices-flexvnf", "flexvnf", "echo test") == "test"

@pytest.mark.test_set2
def test_fortinet():
    assert run_command("devices-fortinet", "fortinet", "echo test") == "test"

@pytest.mark.test_set2
def test_hp_comware():
    assert run_command("devices-hp_comware", "hp_comware", "echo test") == "test"

@pytest.mark.test_set2
def test_huawei():
    assert run_command("devices-huawei", "huawei", "echo test") == "test"

@pytest.mark.test_set2
def test_juniper_junos():
    assert run_command("devices-juniper_junos", "juniper_junos", "echo test") == "test"

@pytest.mark.test_set2
def test_mikrotik_routeros_v6():
    assert run_command("devices-mikrotik_routeros_v6", "mikrotik_routeros", "echo test") == "test"

@pytest.mark.test_set2
def test_mikrotik_routeros_v7():
    assert run_command("devices-mikrotik_routeros_v7", "mikrotik_routeros", "echo test") == "test"

@pytest.mark.test_set2
def test_ubiquiti_edgerouter():
    assert run_command("devices-ubiquiti_edgerouter", "ubiquiti_edgerouter", "echo test") == "test"

@pytest.mark.test_set2
def test_ubiquiti_edgeswitch():
    assert run_command("devices-ubiquiti_edgeswitch", "ubiquiti_edgeswitch", "echo test") == "test"