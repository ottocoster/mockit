from netmiko import ConnectHandler

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
        return net_connect.send_command_timing(command)

test = run_command("192.168.50.128", "accedian", "show test")

print(test)