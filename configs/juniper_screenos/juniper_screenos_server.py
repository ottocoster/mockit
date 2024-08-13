# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/juniper_screenos/juniper_screenos_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class juniper_screenos_server(SSH_Server):
    pass

class juniper_screenos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'juniper_screenos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = ">", alt_terminator = "-")