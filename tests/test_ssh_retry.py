import pytest
import time
from netmiko import ConnectHandler

LOGIN_RETRY=3

def netmiko_login(host, device_type, username="test", password="test", max_retries = 0):
    parameters = {
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
        "verbose": True,
        "fast_cli": False
    }

    for attempt in range(max_retries + 1):
        try:
            connection = ConnectHandler(**parameters)
            return attempt 
        except Exception as e:
            print(f"Login attempt {attempt + 1} failed: {e}")
            if attempt == max_retries:
                pytest.fail(f"Failed to connect after {max_retries} attempts")
    else:
        pytest.fail("Unable to establish a connection")
    connection.disconnect()  # Disconnect the connection after all tests are done

def test_delay():
    global LOGIN_RETRY
    retries = netmiko_login("192.168.233.128", "a10", max_retries=LOGIN_RETRY)
    assert retries == LOGIN_RETRY, f"Login retry test failed. Expected {LOGIN_RETRY} but retried {retries} times."
