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

@pytest.mark.test_set1
def test_a10():
    assert run_command("devices-a10", "a10", "echo test") == "test"

@pytest.mark.test_set1
def test_accedian():
    assert run_command("devices-accedian", "accedian", "echo test") == "test"
