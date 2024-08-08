# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/ruckus_fastiron/ruckus_fastiron_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class ruckus_fastiron_server(SSH_Server):
    pass

class ruckus_fastiron_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'ruckus_fastiron'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")