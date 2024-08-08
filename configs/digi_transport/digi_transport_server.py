# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/digi_transport/digi_transport_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class digi_transport_server(SSH_Server):
    pass

class digi_transport_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'digi_transport'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")