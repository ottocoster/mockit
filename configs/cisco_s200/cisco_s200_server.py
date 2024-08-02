# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/cisco_s200/cisco_s200_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class cisco_s200_server(SSH_Server):
    pass

class cisco_s200_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'cisco_s200'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")