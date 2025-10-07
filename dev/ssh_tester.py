from netmiko import ConnectHandler

def run_command(host, device_type, command, username="test", password="test", secret="secret"):
    parameters = {
        "device_type": device_type,
        "host": host,
        # "username": username,
        # "password": password,
        # "secret": secret,
        "use_keys": True,
        "key_file": "./auth_keys/auth",
    }

    with ConnectHandler(**parameters) as net_connect:
        return net_connect.send_command(command)

test = run_command("192.168.227.128", "a10", "echo test")
print(test)
