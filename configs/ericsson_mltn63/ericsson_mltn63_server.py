# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/ericsson_mltn63/ericsson_mltn63_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class ericsson_mltn63_server(SSH_Server):
    pass

class ericsson_mltn63_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'ericsson_mltn63'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")