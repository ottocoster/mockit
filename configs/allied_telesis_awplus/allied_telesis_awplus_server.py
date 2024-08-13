# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/a10/a10_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class allied_telesis_awplus_server(SSH_Server):
    pass

class allied_telesis_awplus_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'allied_telesis_awplus'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")

    