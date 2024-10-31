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

test = run_command("192.168.56.129", "cisco_ios_telnet", "echo test")

print(test)