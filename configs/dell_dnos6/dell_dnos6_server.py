from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

from src.telnet_server.telnet_handler import Telnet_Handler


raisecom_server = SSH_Server


class raisecom_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'raisecom_roap'
        super().__init__(process, options=options)


class raisecom_telnet_handler(Telnet_Handler):
    def __init__(self, reader, writer, options=None):
        options['device_type'] = 'raisecom'
        super().__init__(reader, writer, options=options or {})
