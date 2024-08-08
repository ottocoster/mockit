from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class calix_b6_server(SSH_Server):
    pass

class calix_b6_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'calix_b6'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")
