# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/cdot_cros/cdot_cros_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class cdot_cros_server(SSH_Server):
    pass

class cdot_cros_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'cdot_cros'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")