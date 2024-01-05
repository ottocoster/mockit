from netmiko import ConnectHandler, platforms  

cisco1 = { 
    "device_type": "cisco_ios",
    "host": "localhost",
    "port": 23,
    "username": "root",
    "password": "test",
    "verbose": True,
    "fast_cli": False
}

with ConnectHandler(**cisco1) as net_connect:      
    raw = net_connect.send_command_timing("echo test")
    print(">>" + raw)