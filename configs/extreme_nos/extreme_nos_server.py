# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/extreme_nos/extreme_nos_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class extreme_nos_server(SSH_Server):
    pass

class extreme_nos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'extreme_nos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern="#")