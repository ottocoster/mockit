from netmiko import ConnectHandler
import pytest

def run_command(host, device_type, command, key_path="./auth_keys/auth"):
    parameters = {
        "device_type": device_type,
        "host": host,
        "use_keys": True,
        "key_file": key_path,
    }

    with ConnectHandler(**parameters) as net_connect:
        return net_connect.send_command(command)
    

@pytest.mark.test_authkey
def test_a10():
    assert run_command("192.168.227.128", "a10", "echo test" ) == "test"
