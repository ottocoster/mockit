from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class infinera_packet_server(SSH_Server):
    pass

class infinera_packet_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'infinera_packet'
        super().__init__(process, options=options)

    