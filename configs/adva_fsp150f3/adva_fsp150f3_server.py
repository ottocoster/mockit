# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/adva_fsp150f3/adva_fsp150f3_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class adva_fsp150f3_server(SSH_Server):
    pass

class adva_fsp150f3_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'adva_fsp150f3'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")