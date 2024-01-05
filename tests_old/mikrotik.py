from netmiko import ConnectHandler, platforms  

cisco1 = { 
    "device_type": "mikrotik_routeros",
    "host": "localhost",
    "port": 25,
    "username": "root",
    "password": "test",
    "verbose": True,
    "fast_cli": False
}

with ConnectHandler(**cisco1) as net_connect:      
    raw = net_connect.send_command_timing("interface bridge host print")
    print(raw)