from pytest_netconf import NetconfServer
from pytest_netconf.sshserver import SSHServer

import paramiko
import threading
import time

import logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to capture all logs, including INFO, WARNING, ERROR, and DEBUG

logger = logging.getLogger(__name__)


class AsyncNetconfServer(NetconfServer):
    def start(self) -> None:
        """
        Start the mock NETCONF server.

        Raises:
            OSError: If the server fails to bind to the specified port.
        """
        self.running = True
        self._bind_socket()
        logger.info("Netconf server started..")
        accept_thread = threading.Thread(target=self._accept_connections)
        accept_thread.start()
        time.sleep(1)  # Give the server a moment to start

    def _accept_connections(self):
        while self.running:
            try:
                self._client_socket, _ = self._server_socket.accept()
                logger.info("Connection accepted.")
                self._thread = threading.Thread(target=self._run)
                self._thread.start()
            except OSError as e:
                logger.error("Error accepting connection: %s", e)

    def _run(self) -> None:
        """Run the server to accept connections and process requests."""
        try:
            transport = paramiko.Transport(self._client_socket)
            transport.add_server_key(paramiko.RSAKey.generate(2048))
            server = SSHServer(self.settings)
            transport.start_server(server=server)
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
            except UnexpectedRequestError as e:
                logger.error("unexpected request error: %s", e)
            except Exception as e:
                msg = "failed to handle request: %s"
                logger.error(msg, e)
                logger.exception(e)
                raise RequestError(msg % e)
                