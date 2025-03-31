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

@pytest.mark.test_set4
def test_adva_fsp150f2():
    assert run_command("devices_adva_fsp150f2", "adva_fsp150f2", "echo test") == "test"

@pytest.mark.test_set4
def test_adva_fsp150f3():
    assert run_command("devices_adva_fsp150f3", "adva_fsp150f3", "echo test") == "test"

@pytest.mark.test_set4
def test_alaxala_ax26s():
    assert run_command("devices_alaxala_ax26s", "alaxala_ax26s", "echo test") == "test"

@pytest.mark.test_set4
def test_alaxala_ax36s():
    assert run_command("devices_alaxala_ax36s", "alaxala_ax36s", "echo test") == "test"

@pytest.mark.test_set4
def test_arris_cer():
    assert run_command("devices_arris_cer", "arris_cer", "echo test") == "test"

@pytest.mark.test_set4
def test_casa_cmts():
    assert run_command("devices_casa_cmts", "casa_cmts", "echo test") == "test"

@pytest.mark.test_set4
def test_cisco_apic():
    assert run_command("devices_cisco_apic", "cisco_apic", "echo test") == "test"

@pytest.mark.test_set4
def test_cisco_s200():
    assert run_command("devices_cisco_s200", "cisco_s200", "echo test") == "test"

@pytest.mark.test_set4
def test_digi_transport():
    assert run_command("devices_digi_transport", "digi_transport", "echo test") == "test"

@pytest.mark.test_set4
def test_ericsson_mltn63():
    assert run_command("devices_ericsson_mltn63", "ericsson_mltn63", "echo test") == "test"

@pytest.mark.test_set4
def test_ericsson_mltn66():
    assert run_command("devices_ericsson_mltn66", "ericsson_mltn66", "echo test") == "test"

@pytest.mark.test_set4
def test_fiberstore_fsos():
    assert run_command("devices_fiberstore_fsos", "fiberstore_fsos", "echo test") == "test"

@pytest.mark.test_set4
def test_garderos_grs():
    assert run_command("devices_garderos_grs", "garderos_grs", "echo test") == "test"

@pytest.mark.test_set4
def test_hillstone_stoneos():
    assert run_command("devices_hillstone_stoneos", "hillstone_stoneos", "echo test") == "test"

@pytest.mark.test_set4
def test_huawei_vrp():
    assert run_command("devices_huawei_vrp", "huawei_vrp", "echo test") == "test"

@pytest.mark.test_set4
def test_juniper():
    assert run_command("devices_juniper", "juniper", "echo test") == "test"

@pytest.mark.test_set4
def test_ubiquiti_edge():
    assert run_command("devices_ubiquiti_edge", "ubiquiti_edge", "echo test") == "test"

@pytest.mark.test_set4
def test_vertiv_mph():
    assert run_command("devices_vertiv_mph", "vertiv_mph", "echo test") == "test"
