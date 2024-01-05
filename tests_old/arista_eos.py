from netmiko import ConnectHandler, platforms

parameters = { 
    "device_type": "cisco_wlc",
    "host": "localhost",
    "port": 22,
    "username": "root",
    "password": "test",
    "verbose": True,
    "fast_cli": False
}

with ConnectHandler(**parameters) as net_connect:      
    raw = net_connect.send_command_timing("echo test")
    print("<<" + raw)