from netmiko import ConnectHandler
import pytest
def run_command(host, device_type, command, username="test", password="test"):
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
    assert run_command("192.168.112.128", "a10", "echo test") == "test"
