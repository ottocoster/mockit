# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/casa_cmts/casa_cmts_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class casa_cmts_server(SSH_Server):
    pass

class casa_cmts_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'casa_cmts'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")