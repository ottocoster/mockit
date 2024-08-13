# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/dell_os6/dell_os6_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class dell_os6_server(SSH_Server):
    pass

class dell_os6_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'dell_os6'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")