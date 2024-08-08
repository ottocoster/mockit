# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/extreme_ers/extreme_ers_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class extreme_ers_server(SSH_Server):
    pass

class extreme_ers_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'extreme_ers'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")