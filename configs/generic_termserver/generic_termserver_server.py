# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/generic_termserver/generic_termserver_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class generic_termserver_server(SSH_Server):
    pass

class generic_termserver_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'generic_termserver'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")