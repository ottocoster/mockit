# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/a10/a10_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class apresia_aeos_server(SSH_Server):
    pass

class apresia_aeos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'apresia_aeos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")
