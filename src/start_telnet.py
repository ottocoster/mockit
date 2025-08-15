import logging
import importlib
import asyncio

from src.options import get_normalized_device_type
from src.telnet_server.telnet_handler import Telnet_Handler  # Default handler

logger = logging.getLogger("app")


def load_telnet_handler(device_type, device_version):
    """
    Dynamically load the Telnet handler class for a specific device.

    Args:
        device_type (str): Type of the device.
        device_version (str): Version of the device (optional).

    Returns:
        class: Handler class for the specified device type.
    """
    normalized = get_normalized_device_type(device_type)

    try:
        # Dynamically import the module based on the device type
        if device_version:
            module = importlib.import_module(
                f"configs.{normalized}.{device_version}.{normalized}_{device_version}_server"
            )
        else:
            module = importlib.import_module(
                f"configs.{normalized}.{normalized}_server"
            )

        # Get the server and handler classes from the module
        handler_class = getattr(module, f"{normalized}_telnet_handler")
        logger.debug(
            f"Loaded Telnet handler for {device_type} (version: {device_version})"
        )
        return handler_class
    except (ModuleNotFoundError, AttributeError) as e:
        logger.warning(
            f"Specific Telnet handler for {device_type} not found. Falling back to default handler."
        )
        return Telnet_Handler


# def handle_client(conn, addr, options, handler_class):
#     """
#     Handle an incoming client connection.
#
#     Args:
#         conn (socket.socket): Client connection.
#         addr (tuple): Client address.
#         options (dict): Server configuration options.
#     """
#     logger.info(f"Connection established with {addr}")
#
#     # Create an instance of the handler
#     handler = handler_class(conn, options)
#     handler.run()
#

async def start_telnet(status, options):
    """
    Start the Telnet server asynchronously.
    """
    device_type = options.get("device_type")
    device_version = options.get("device_version")
    handler_class = load_telnet_handler(device_type, device_version)

    async def accept_client(reader, writer):
        """
        Accept a client connection and pass the async reader/writer to the handler.
        """
        addr = writer.get_extra_info("peername")
        logger.info(f"Connection established with {addr}")
        handler = handler_class(reader, writer, options)
        await handler.run()

    server = await asyncio.start_server(accept_client, host=None, port=23)
    await status.service_ready()
    addr = server.sockets[0].getsockname()
    logger.info(f"Telnet server running on {addr}")

    async with server:
        await server.serve_forever()
