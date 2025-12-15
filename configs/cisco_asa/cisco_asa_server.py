from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class cisco_asa_server(SSH_Server):
    pass

class cisco_asa_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'cisco_asa'
        super().__init__(process, options=options)

    