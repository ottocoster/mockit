from netmiko import ConnectHandler, platforms  

cisco1 = { 
    "device_type": "juniper_junos",
    "host": "localhost",
    "username": "root",
    "password": "test",
    "verbose": True,
    "fast_cli": False
}

with ConnectHandler(**cisco1) as net_connect:      
    raw = net_connect.send_command_timing("show interfaces")
    print(raw)