from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class vertiv_mph_server(SSH_Server):
    pass

class vertiv_mph_handler(SSH_Handler):
    def __init__(self, process: SSHS
    erverProcess, options):
        options['device_type'] = 'vertiv_mph'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "cli->", alt_terminator = "cli->")