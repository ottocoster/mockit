# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/sophos_sfos/sophos_sfos_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class sophos_sfos_server(SSH_Server):
    pass

class sophos_sfos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'sophos_sfos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern="#>")