from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class bintec_boss_server(SSH_Server):
    pass

class bintec_boss_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'bintec_boss'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = ">", alt_terminator = ">")
