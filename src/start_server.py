import logging
import asyncssh
from asyncssh.process import SSHServerProcess
from netmiko import ConnectHandler
import importlib

server_class = None
handler_class = None

def load_device_classes(device_type):
    """
    Dynamically load device-specific server and handler classes.

    Args:
        device_type (str): Type of the device.

    Returns:
        tuple: Server and handler classes for the specified device type.
    """
    try:
        # Dynamically import the module based on the device type
        module = importlib.import_module(f'configs.{device_type}.{device_type}_server')
        # Get the server and handler classes from the module
        server_class = getattr(module, f'{device_type}_server')
        handler_class = getattr(module, f'{device_type}_handler')
    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"Unsupported device type: {device_type}") from e

    return server_class, handler_class

async def start_server(options):
    """
    Start the SSH server with the provided options.

    Args:
        options (dict): Configuration options for the server.
    """
    global server_class, handler_class
    logger = logging.getLogger()
    
    # Load device-specific server and handler classes
    server_class, handler_class = load_device_classes(options["device_type"])

    # Set up parameters for ConnectHandler
    parameters = {
        "device_type": options["device_type"],
        "host": "localhost",
        "username": options["username"],
        "password": options["password"],
        "auto_connect": False
    }

    # Modify connection parameters using netmiko
    with ConnectHandler(**parameters) as net_connect:
        net_connect._modify_connection_params()
        if not options["device_type"].startswith("ericsson_mltn"):
            options["username"] = net_connect.username
            options["password"] = net_connect.password
        options["new_line"] = net_connect.RETURN

    logger.debug(f"Using SSH options: {options}")

    # Create and start the async SSH server
    await asyncssh.create_server(
        server_factory=lambda: server_class(options, logger),
        host="0.0.0.0",
        port=22,
        server_host_keys=options["ssh_key"],
        process_factory=create_session,
        line_echo=False,
        line_editor=True
    )

async def create_session(process: SSHServerProcess):
    """
    Create a new SSH session.

    Args:
        process (SSHServerProcess): SSH server process instance.
    """
    session = handler_class(process, process.get_extra_info("options"))
    await session.open()
