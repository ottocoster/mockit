from netmiko import ConnectHandler
import pytest

def run_command(host, device_type, command, username="test", password="test"):
    parameters = {
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
    }

    with ConnectHandler(**parameters) as net_connect:
        return net_connect.send_command(command)

test = run_command("192.168.106.128", "sophos_sfos", "echo test")
print(test)
