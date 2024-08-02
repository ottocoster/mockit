# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/dell_dnos9/dell_dnos9_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class dell_dnos9_server(SSH_Server):
    pass

class dell_dnos9_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'dell_dnos9'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")