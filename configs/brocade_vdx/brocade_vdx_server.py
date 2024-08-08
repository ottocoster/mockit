from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class brocade_vdx_server(SSH_Server):
    pass

class brocade_vdx_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'brocade_vdx'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")

    