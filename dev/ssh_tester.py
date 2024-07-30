from netmiko import ConnectHandler
import re

def run_command(host, device_type, command, username="test", password="test"):
    parameters = {
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password,
        "secret": password,
        "verbose": True,
        "fast_cli": False
    }

    with ConnectHandler(**parameters) as net_connect:
        output = net_connect.send_command_timing(command, strip_prompt=True, strip_command=True)
        # Using regular expression to extract only the command output if automatic strip output failed
        match = re.search(r'^.*# .*?\n(.+)$', output, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return output

test = run_command("192.168.112.128", "apresia_aeos", "show test")

print(test)