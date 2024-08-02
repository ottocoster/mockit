# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/ericsson_ipos/ericsson_ipos_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class ericsson_ipos_server(SSH_Server):
    pass

class ericsson_ipos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'ericsson_ipos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")