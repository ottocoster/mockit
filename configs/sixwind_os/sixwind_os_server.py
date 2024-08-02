# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/sixwind_os/sixwind_os_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class sixwind_os_server(SSH_Server):
    pass

class sixwind_os_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'sixwind_os'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")