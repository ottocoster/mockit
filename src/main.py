import asyncio
import logging
import signal
from asyncio import Event, Runner

from snmp_server import asyncsnmp_server
from src import logconf  # noqa
from src.options import get_options, get_overridden_options
from src.services import ServerRegistry, is_valid_platform
from src.start_netconf import start_netconf, stop_netconf
from src.start_ssh import start_ssh
from src.start_telnet import start_telnet


logger = logging.getLogger(__name__)
server_registry = ServerRegistry()


def restart_handler(signum, frame):
    if server_registry is not None:
        print(f'Received restart signal {signum}')
        server_registry.restart()


async def main() -> bool:
    get_overridden_options.cache_clear()
    options = get_options()
    logger.debug(f"Options: {options}")
    udp_reload_port = options['UDP_RELOAD_PORT']
    enable_reload = options['ENABLE_RELOAD']

    # Fetch device type from environment variable
    device_type = options.get("DEVICE_TYPE")
    device_version = options.get("DEVICE_VERSION")

    if is_valid_platform(device_type, device_version):
        # Register all servers with their configurations
        server_registry.register("telnet", start_telnet, options)
        server_registry.register("snmp", asyncsnmp_server.start_server, options, asyncsnmp_server.stop_server)
        server_registry.register("netconf", start_netconf, options, stop_netconf)
        server_registry.register("ssh", start_ssh, options)
    else:
        logger.error(f"Device type `{device_type}` is not valid!")
        if not enable_reload:
            return False
    try:
        return await server_registry.start_all(enable_reload, udp_reload_port)
    except Exception as e:
        logger.error(f"Error starting servers: {e}")
        return False
    finally:
        # Graceful shutdown
        await server_registry.shutdown_all()
        # Cancel any remaining tasks
        for task in asyncio.all_tasks():
            if not task.done() and task != asyncio.current_task():
                task.cancel()


if __name__ == "__main__":
    signal.signal(signal.SIGUSR1, restart_handler)  # Custom restart signal
    working = True
    while working:
        with Runner(debug=True) as runner:
            working = runner.run(main())
