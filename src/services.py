import asyncio
import logging
import os
from asyncio import Event
from pathlib import Path
from typing import Any, Callable
from dataclasses import dataclass

from src.options import extract_options


logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Configuration for a registered server"""
    start_func: Callable
    shutdown_func: Callable | None
    options: dict[str, Any]
    enabled: bool


class ServiceStatus:
    def __init__(self, parties: int):
        self.lock = asyncio.Lock()
        self.parties = parties
        self.services_started = 0
        self.ready_event = asyncio.Event()

    async def service_ready(self):
        async with self.lock:
            self.services_started += 1
            if self.services_started == self.parties:
                self.ready_event.set()


class ServerRegistry:
    restart_event: Event | None = None
    restart_sender: tuple[str, int] | None = None
    status: ServiceStatus | None = None

    def __init__(self):
        self.servers: dict[str, ServerConfig] = {}
        self.running_tasks: dict[str, asyncio.Task] = {}

    def register(
            self,
            name: str,
            start_func: Callable,
            options: dict[str, Any],
            shutdown_func: Callable | None = None
    ):
        """Register a server with its configuration"""
        service_options = options.get(name)
        enabled = options[f"{name.upper()}_SERVER_ENABLED"]
        self.servers[name] = ServerConfig(
            start_func=start_func,
            shutdown_func=shutdown_func,
            options=service_options,
            enabled=enabled
        )

    def get_enabled_parties(self) -> set[str]:
        return {k for k, v in self.servers.items() if v.enabled}

    async def start_all(self, enable_reload: bool, udp_reload_port:int = 0) -> bool:
        """Start all enabled servers and return their tasks"""
        logger.info("Starting services...")
        tasks: list[asyncio.Task] = []
        self.status = status = ServiceStatus(len(self.get_enabled_parties()))

        for name, config in self.servers.items():
            if config.enabled:
                logger.debug(f"Starting {name} ...")
                task = asyncio.create_task(
                    config.start_func(status, config.options),
                    name=f"server_{name}"
                )
                self.running_tasks[name] = task
                tasks.append(task)
                # Add a small delay between server starts to avoid race conditions
                await asyncio.sleep(0.1)
        signal_task = None
        if enable_reload:
            self.restart_event = Event()
            signal_task = asyncio.create_task(
                self.restart_event.wait(), name="restart_monitor")
            tasks.append(signal_task)
            if udp_reload_port:
                coro = self.listen_for_udp_reload(udp_reload_port)
                udp_restart_task = asyncio.create_task(coro, name="udp_restart")
                tasks.append(udp_restart_task)
            if self.restart_sender:
                asyncio.create_task(self.acknowledge_restart())
        logger.info("Services started successfully.")
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        should_restart = signal_task and signal_task in done
        return should_restart

    async def shutdown_all(self):
        """Gracefully shutdown all running servers"""
        logger.info("Shutting down service...")
        self.restart_event = None
        self.stop_all()
        await self.cancel_tasks()
        self.running_tasks.clear()
        self.servers.clear()
        logger.info("All services shut down successfully.")

    def stop_all(self):
        # Call shutdown functions first
        for name in reversed(self.servers):
            config = self.servers[name]
            if name in self.running_tasks and config.shutdown_func:
                try:
                    config.shutdown_func()
                except Exception as e:
                    print(f"Error calling shutdown function for {name}: {e}")

    async def cancel_tasks(self):
        # Then cancel tasks
        shutdown_tasks = []
        for name, task in self.running_tasks.items():
            if not task.done():
                task.cancel()
                shutdown_tasks.append(task)

        if shutdown_tasks:
            # Wait for all tasks to complete gracefully
            await asyncio.sleep(.1)
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)

    async def listen_for_udp_reload(self, port: int):
        """Listen on a specific UDP port and set restart_event when data is received"""
        assert self.restart_event is not None
        if self.status.parties:
            logger.info("Waiting for services to be ready")
            await self.status.ready_event.wait()
        logger.debug(f"Setting up the UDP listener on port {port}")
        try:
            loop = asyncio.get_event_loop()
            # Create endpoint with DatagramProtocol
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: RestartTriggerProtocol(self),
                local_addr=('0.0.0.0', port), reuse_port=True
            )
            try:
                # Wait until restart_event is set (by the protocol)
                await self.restart_event.wait()
                logging.info("Restart event triggered, shutting down UDP listener")
            finally:
                transport.close()
        except Exception as e:
            logging.error(f"Error starting restart trigger UDP listener on port:{port}: {e}")

    async def acknowledge_restart(self):
        # Send UDP acknowledgment to the restart sender asynchronously
        restart_sender, self.restart_sender = self.restart_sender, None
        if not restart_sender:
            logger.debug("No restart sender found, skipping UDP acknowledgment")
            return
        await self.status.ready_event.wait()
        try:
            loop = asyncio.get_event_loop()
            transport, _ = await loop.create_datagram_endpoint(
                asyncio.DatagramProtocol,
                remote_addr=restart_sender
            )
            try:
                message = b"Services restarted successfully"
                transport.sendto(message)
                logger.info(f"Sent restart acknowledgment to {restart_sender}")
            finally:
                transport.close()
        except Exception as e:
            logger.error(f"Failed to send restart acknowledgment to {restart_sender}: {e}")

    def restart(self, restart_sender: tuple[str, int] | None = None):
        """Trigger a restart event"""
        if self.restart_event:
            self.restart_sender = restart_sender
            if (loop := self.restart_event._get_loop()) and not loop.is_closed():
                loop.call_soon_threadsafe(self.restart_event.set)


class RestartTriggerProtocol(asyncio.DatagramProtocol):
    def __init__(self, registry: ServerRegistry):
        self.registry = registry
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        logging.info(f"Restart trigger UDP listener ready on {transport.get_extra_info('sockname')}")

    def datagram_received(self, data, addr):
        from healthcheck import HEALTH_CHECK_MSG
        if data and data.startswith(HEALTH_CHECK_MSG):
            logger.info(f"Health check from {addr}")
            self.transport.sendto(data, addr)
            return

        content = data.decode('utf-8', errors='ignore')
        new_options = extract_options(content)
        if device_type := new_options.get("DEVICE_TYPE"):
            version = new_options.get("DEVICE_VERSION", os.environ.get("DEVICE_VERSION"))
            if not is_valid_platform(device_type, version):
                logging.warning(f"Invalid device type or version: {device_type} {version}")
                new_options["DEVICE_TYPE"] = ''
        os.environ.update(new_options)
        logger.debug(f"New environment variables: {os.environ}")
        logging.info(f"Restart trigger received from {addr}:\n{content}")
        # Set the restart event
        if self.registry:
            self.registry.restart(addr)

    def error_received(self, exc):
        logging.error(f"UDP error received: {exc}")


def is_valid_platform(device_type: str, device_version: str | None = None) -> bool:
    if not device_type:
        return False
    normalized_type = device_type.removesuffix("_ssh").removesuffix("_telnet")
    device_dir = Path(f"configs/{normalized_type}")
    if device_version:
        device_dir /= device_version
    supported = device_dir.exists() and device_dir.is_dir()
    return supported
