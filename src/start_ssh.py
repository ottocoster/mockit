import logging
import asyncssh
from asyncssh.process import SSHServerProcess
from netmiko import ConnectHandler
import importlib


logger = logging.getLogger(__name__)


def load_device_classes(device_type, device_version):
    """
    Dynamically load device-specific server and handler classes.

    Args:
        device_type (str): Type of the device.

    Returns:
        tuple: Server and handler classes for the specified device type.
    """
    if device_version:
        mod = f"configs.{device_type}.{device_version}.{device_type}_{device_version}_server"
    else:
        mod = f"configs.{device_type}.{device_type}_server"
    try:
        # Dynamically import the module based on the device type
        module = importlib.import_module(mod)

        # Get the server and handler classes from the module
        server_class = getattr(module, f'{device_type}_server')
        handler_class = getattr(module, f'{device_type}_handler')
    except (ModuleNotFoundError, AttributeError) as e:
        raise ValueError(f"Unsupported device type: {device_type}") from e

    return server_class, handler_class


async def start_ssh(status, options):
    """
    Start the SSH server with the provided options.

    Args:
        options (dict): Configuration options for the server.
    """
    logger.debug(f"starting ssh {options}")

    # Load device-specific server and handler classes
    server_class, handler_class = load_device_classes(options["device_type"], options["device_version"])

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
    logger.debug(f"authkey_enabled: {options["authkey_enabled"]}")

    key_opt = {}
    if options["authkey_enabled"]:
        key_opt = dict(authorized_client_keys=options["authkey_path"])

    # Support restricting key exchange algorithms and ciphers for compatibility testing.
    kex_algorithms = [alg.strip() for alg in options.get("kex_algorithms", "").split(",") if alg.strip()]
    if kex_algorithms:
        key_opt["kex_algs"] = kex_algorithms

    ciphers = [alg.strip() for alg in options.get("ciphers", "").split(",") if alg.strip()]
    if ciphers:
        key_opt["encryption_algs"] = ciphers

    async def handle_connection(process: SSHServerProcess):
        session = handler_class(process, process.get_extra_info("options"))
        await session.open()

    # Create and start the async SSH server
    server = await asyncssh.create_server(
        server_factory=lambda: server_class(options, logger),
        host=["::", "0.0.0.0"],
        port=options['port'],
        server_host_keys=options["ssh_key"],
        process_factory=handle_connection,
        line_echo=False,
        line_editor=True,
        reuse_address=True,
        **key_opt
    )
    await status.service_ready()
    await server.wait_closed()
