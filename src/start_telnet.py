import socket
import threading
import logging
import importlib
from src.telnet_server.telnet_handler import Telnet_Handler  # Default handler

# Server Configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 23  # Default Telnet port, but requires admin rights to run on Unix-based OS

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

def load_telnet_handler(device_type, device_version):
    """
    Dynamically load the Telnet handler class for a specific device.

    Args:
        device_type (str): Type of the device.
        device_version (str): Version of the device (optional).

    Returns:
        class: Handler class for the specified device type.
    """
    try:
       
        # Dynamically import the module based on the device type
        if device_version:
            module = importlib.import_module(f'configs.{device_type}.{device_version}.{device_type}_{device_version}_server')
        else:
            module = importlib.import_module(f'configs.{device_type}.{device_type}_server')

        # Get the server and handler classes from the module
        handler_class = getattr(module, f'{device_type}_telnet_handler')
        logger.debug(f"Loaded Telnet handler for {device_type} (version: {device_version})")
        return handler_class
    except (ModuleNotFoundError, AttributeError) as e:
        logger.warning(f"Specific Telnet handler for {device_type} not found. Falling back to default handler.")
        return Telnet_Handler

def handle_client(conn, addr, options, handler_class):
    """
    Handle an incoming client connection.

    Args:
        conn (socket.socket): Client connection.
        addr (tuple): Client address.
        options (dict): Server configuration options.
    """
    logger.info(f"Connection established with {addr}")

    # Create an instance of the handler
    handler = handler_class(conn, options)
    handler.run()

def start_telnet(options):
    """
    Start the Telnet server.

    Args:
        options (dict): Configuration options for the server.
    """
    device_type = options.get("device_type")
    device_version = options.get("device_version")
    handler_class = load_telnet_handler(device_type, device_version)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    logger.info(f"Telnet server running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr, options, handler_class)).start()
