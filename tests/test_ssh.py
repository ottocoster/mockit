from netmiko import ConnectHandler, platforms  

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
        return net_connect.send_command_timing(command)

def test_arista_eos():
    assert run_command("devices-arista_eos", "arista_eos", "echo test") == "test"

def test_aruba_os():
    assert run_command("devices-aruba_os", "aruba_os", "echo test") == "test"

def test_cisco_asa():
    assert run_command("devices-cisco_asa", "cisco_asa", "echo test") == "test"

def test_cisco_ios():
    assert run_command("devices-cisco_ios", "cisco_ios", "echo test") == "test"

def test_cisco_nxos():
    assert run_command("devices-cisco_nxos", "cisco_nxos", "echo test") == "test"

# def test_cisco_wlc():
#     assert run_command("devices-cisco_wlc", "cisco_wlc", "echo test") == "test"

def test_cisco_xr():
    assert run_command("devices-cisco_xr", "cisco_xr", "echo test") == "test"

def test_fortinet():
    assert run_command("devices-fortinet", "fortinet", "echo test") == "test"

def test_hp_comware():
    assert run_command("devices-hp_comware", "hp_comware", "echo test") == "test"

# def test_huawei():
#     assert run_command("devices-huawei", "huawei", "echo test") == "test"

def test_juniper_junos():
    assert run_command("devices-juniper_junos", "juniper_junos", "echo test") == "test"

def test_mikrotik_routeros_v6():
    assert run_command("devices-mikrotik_routeros_v6", "mikrotik_routeros", "echo test") == "test"

def test_mikrotik_routeros_v7():
    assert run_command("devices-mikrotik_routeros_v7", "mikrotik_routeros", "echo test") == "test"

def test_ubiquiti_edgerouter():
    assert run_command("devices-ubiquiti_edgerouter", "ubiquiti_edgerouter", "echo test") == "test"

def test_ubiquiti_edgeswitch():
    assert run_command("devices-ubiquiti_edgeswitch", "ubiquiti_edgeswitch", "echo test") == "test"