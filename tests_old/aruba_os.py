from netmiko import ConnectHandler, platforms

parameters = { 
    "device_type": "aruba_os",
    "host": "localhost",
    "port": 24,
    "username": "root",
    "password": "test",
    "verbose": True,
    "fast_cli": False
}

with ConnectHandler(**parameters) as net_connect:      
    raw = net_connect.send_command_timing("echo test")
    print("<<" + raw)