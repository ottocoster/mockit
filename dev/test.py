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

def test_audiocode_shell():
    assert run_command("192.168.233.128", "juniper_screenos", "echo test") == "test"
    