import logging
import asyncssh
from asyncssh.process import SSHServerProcess
from netmiko import ConnectHandler  

from ssh_server.ssh_session import SSHSession
import importlib

server_class = None
handler_class = None

def load_device_classes(device_type):
    try:
        # Dynamically import the module based on the device type
        module = importlib.import_module(f'configs.{device_type}.{device_type}_server')
        
        print("module", module)
        # Dynamically get the classes from the module
        server_class = getattr(module, f'{device_type}_server')
        handler_class = getattr(module, f'{device_type}_handler')

        
        print("handler_class", handler_class)
    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"Unsupported device type: {device_type}") from e

    return server_class, handler_class



async def start_server(options):
    global server_class, handler_class
    logger = logging.getLogger()
    server_class, handler_class = load_device_classes(options["device_type"])

    parameters = { 
        "device_type": options["device_type"],
        "host": "localhost",
        "username": options["username"],
        "password": options["password"],
        "auto_connect": False
    }

    with ConnectHandler(**parameters) as net_connect:      
        net_connect._modify_connection_params()
        options["username"] = net_connect.username
        options["password"] = net_connect.password
        options["new_line"] = net_connect.RETURN

    logger.debug(f"Using ssh options: {options}")
    await asyncssh.create_server(
        server_factory=lambda: server_class(options, logger),
        host="0.0.0.0",
        port=22,
        server_host_keys=options["ssh_key"],
        process_factory=create_session,
        line_echo=False,
        line_editor=len(options["echo_format"]) == 0
    )

async def create_session(process: SSHServerProcess):
    session = handler_class(process, process.get_extra_info("options"))
    await session.open()


async def create_session2(process: SSHServerProcess):
    session = SSHSession(process, process.get_extra_info("options"))
    await session.open()