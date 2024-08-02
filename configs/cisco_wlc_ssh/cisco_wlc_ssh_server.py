# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/cisco_wlc_ssh/cisco_wlc_ssh_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class cisco_wlc_ssh_server(SSH_Server):
    pass

class cisco_wlc_ssh_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'cisco_wlc_ssh'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")