# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/watchguard_firebox/watchguard_firebox_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class watchguard_firebox_server(SSH_Server):
    pass

class watchguard_firebox_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'watchguard_firebox'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")