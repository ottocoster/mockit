import pytest
import time
from netmiko import ConnectHandler

LOGIN_DELAY=3
DEVICE_DELAY=2

def run_command(host, device_type, command, username="test", password="test"):
    parameters = {
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
        "verbose": True,
        "fast_cli": False
    }

    # Measure login time
    start_login_time = time.time()

    try:
        with ConnectHandler(**parameters) as net_connect:
            end_login_time = time.time()
            login_time = end_login_time - start_login_time

            # Measure command execution time
            start_command_time = time.time()
            output = net_connect.send_command("echo test")
            end_command_time = time.time()
            
            command_time = end_command_time - start_command_time
            return login_time, command_time, output

    except Exception as e:
        pytest.fail(f"Test failed due to exception: {e}")

def test_delay():
    global LOGIN_DELAY, DEVICE_DELAY
    login_time, command_time, output = run_command("192.168.233.128", "a10", "echo test")
    assert login_time > LOGIN_DELAY, f"Login delay test failed. Expected {LOGIN_DELAY}s but takes {login_time}"
    assert command_time > DEVICE_DELAY, f"Command delay test failed. Expected {DEVICE_DELAY}s but takes {command_time}"
    assert output == "test", f"Command output test failed. Expected 'test' but got {output}"

