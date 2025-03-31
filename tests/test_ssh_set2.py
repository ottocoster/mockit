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
    assert run_command("devices_dell_dnos9", "dell_dnos9", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_force10():
    assert run_command("devices_dell_force10", "dell_force10", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_isilon():
    assert run_command("devices_dell_isilon", "dell_isilon", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_os6():
    assert run_command("devices_dell_os6", "dell_os6", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_os9():
    assert run_command("devices_dell_os9", "dell_os9", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_os10():
    assert run_command("devices_dell_os10", "dell_os10", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_powerconnect():
    assert run_command("devices_dell_powerconnect", "dell_powerconnect", "echo test") == "test"

@pytest.mark.test_set2
def test_dell_sonic():
    assert run_command("devices_dell_sonic", "dell_sonic", "echo test") == "test"

@pytest.mark.test_set2
def test_digi_transport():
    assert run_command("devices_digi_transport", "digi_transport", "echo test") == "test"

@pytest.mark.test_set2
def test_dlink_ds():
    assert run_command("devices_dlink_ds", "dlink_ds", "echo test") == "test"

@pytest.mark.test_set2
def test_eltex():
    assert run_command("devices_eltex", "eltex", "echo test") == "test"

@pytest.mark.test_set2
def test_eltex_esr():
    assert run_command("devices_eltex_esr", "eltex_esr", "echo test") == "test"

@pytest.mark.test_set2
def test_endace():
    assert run_command("devices_endace", "endace", "echo test") == "test"

@pytest.mark.test_set2
def test_enterasys():
    assert run_command("devices_enterasys", "enterasys", "echo test") == "test"

@pytest.mark.test_set2
def test_ericsson_ipos():
    assert run_command("devices_ericsson_ipos", "ericsson_ipos", "echo test") == "test"

@pytest.mark.test_set2
def test_ericsson_mltn63():
    assert run_command("devices_ericsson_mltn63", "ericsson_mltn63", "echo test") == "test"

@pytest.mark.test_set2
def test_ericsson_mltn66():
    assert run_command("devices_ericsson_mltn66", "ericsson_mltn66", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme():
    assert run_command("devices_extreme", "extreme", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_ers():
    assert run_command("devices_extreme_ers", "extreme_ers", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_exos():
    assert run_command("devices_extreme_exos", "extreme_exos", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_netiron():
    assert run_command("devices_extreme_netiron", "extreme_netiron", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_nos():
    assert run_command("devices_extreme_nos", "extreme_nos", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_slx():
    assert run_command("devices_extreme_slx", "extreme_slx", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_tierra():
    assert run_command("devices_extreme_tierra", "extreme_tierra", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_vdx():
    assert run_command("devices_extreme_vdx", "extreme_vdx", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_vsp():
    assert run_command("devices_extreme_vsp", "extreme_vsp", "echo test") == "test"

@pytest.mark.test_set2
def test_extreme_wing():
    assert run_command("devices_extreme_wing", "extreme_wing", "echo test") == "test"

@pytest.mark.test_set2
def test_f5_linux():
    assert run_command("devices_f5_linux", "f5_linux", "echo test") == "test"

@pytest.mark.test_set2
def test_f5_ltm():
    assert run_command("devices_f5_ltm", "f5_ltm", "echo test") == "test"

@pytest.mark.test_set2
def test_f5_tmsh():
    assert run_command("devices_f5_tmsh", "f5_tmsh", "echo test") == "test"

@pytest.mark.test_set2
def test_fiberstore_fsos():
    assert run_command("devices_fiberstore_fsos", "fiberstore_fsos", "echo test") == "test"

@pytest.mark.test_set2
def test_flexvnf():
    assert run_command("devices_flexvnf", "flexvnf", "echo test") == "test"

@pytest.mark.test_set2
def test_fortinet():
    assert run_command("devices_fortinet", "fortinet", "echo test") == "test"

@pytest.mark.test_set2
def test_generic():
    assert run_command("devices_generic", "generic", "echo test") == "test"

@pytest.mark.test_set2
def test_generic_termserver():
    assert run_command("devices_generic_termserver", "generic_termserver", "echo test") == "test"
