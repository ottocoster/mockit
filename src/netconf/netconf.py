import asyncio
import os
import socket
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET

from pytest_netconf import NetconfServer
from pytest_netconf.exceptions import RequestError
from pytest_netconf.sshserver import SSHServer

import paramiko

import logging

logger = logging.getLogger('app')


class AsyncNetconfServer(NetconfServer):
    transport = None

    def __init__(self, status):
        super().__init__()
        self.status = status

    async def start(self) -> None:
        """
        Start the mock NETCONF server.

        Raises:
            OSError: If the server fails to bind to the specified port.
        """
        self.running = True
        self._bind_socket()
        await self.status.service_ready()
        logger.info("Netconf server started..")
        await asyncio.to_thread(self._run)
        logger.info("Netconf thread finished")

    def _bind_socket(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )
        self._server_socket.settimeout(1.0)
        self._server_socket.bind((self.settings.host, self.settings.port))
        logger.debug('server socket bound')
        self._server_socket.listen(1)
        logger.debug('server socket listening')

    def stop(self) -> None:
        """Stop the NETCONF server."""
        self.running = False
        if self._server_socket:
            self._server_socket.close()
        if self._client_socket:
            self._client_socket.close()
        if self.transport:
            self.transport.completion_event.set()
            self.transport.close()
        logger.info("Netconf server stopped.")

    def _accept_connections(self):
        while self.running:
            try:
                self._client_socket, _ = self._server_socket.accept()
                logger.info("Connection accepted.")
                # Handle connection...
            except socket.timeout:
                # Timeout occurred, check if we should continue
                continue
            except OSError as e:
                if self.running:  # Only log if we're still supposed to be running
                    logger.error("Error accepting connection: %s", e)
                break
        return self.running

    def _run(self) -> None:
        """Run the server to accept connections and process requests."""
        transport, channel = None, None
        try:
            if not self._accept_connections():
                return
            self._client_socket, _ = self._server_socket.accept()
            transport = paramiko.Transport(self._client_socket)
            transport.add_server_key(paramiko.RSAKey.generate(2048))
            server = SSHServer(self.settings)
            self.transport.start_server(server=server)
            channel = transport.accept(20)

            if channel is None:
                logger.error("channel was not created")
                return

            # Wait for the subsystem request
            server.event.wait(10)

            if server.event.is_set():
                self._handle_requests(channel)

        finally:
            if channel:
                try:
                    channel.close()
                except EOFError:  # pragma: no cover
                    pass
            if transport:
                transport.close()


    def _handle_requests(self, channel: paramiko.Channel) -> None:
        """
        Handle incoming requests on the channel.

        Args:
            channel (paramiko.Channel): The communication channel with the client.
        """
        buffer = bytearray()
        print("respones[]:", self.responses)
        self._hello_sent = False
        while self.running:
            try:
                # Send hello
                if not self._hello_sent:
                    channel.sendall(
                        NetconfServer.BASE_10_TEMPLATE.format(
                            content=self._hello_response()
                        ).encode()
                    )
                    self._hello_sent = True

                data = channel.recv(4096)
                if not data:
                    break
                buffer.extend(data)
                logger.debug("received data: %s", data.decode())
                while True:
                    processed = self._process_buffer(buffer, channel)
                    if not processed:
                        break
            except Exception as e:
                msg = "failed to handle request: %s"
                logger.error(msg, e)
                logger.exception(e)
                raise RequestError(msg % e)

    def get_template(self, tag: str) -> str:
        path = Path('configs') / os.environ['DEVICE_TYPE'] / 'netconf' / f"{tag}.xml"
        return path.read_text() if path.exists() else ''

    def _get_response(self, request: str) -> Optional[str]:
        try:
            xmlrq = ET.fromstring(request).find('.')
            nstag = list(xmlrq.iter())[1].tag
            tag = nstag.split('}')[-1]
            if response := self.get_template(tag):
                return response
        except Exception:
            return super()._get_response(request)
