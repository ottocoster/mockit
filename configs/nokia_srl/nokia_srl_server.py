# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/nokia_srl/nokia_srl_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class nokia_srl_server(SSH_Server):
    pass

class nokia_srl_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'nokia_srl'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = "#")