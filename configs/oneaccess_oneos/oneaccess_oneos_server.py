# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/oneaccess_oneos/oneaccess_oneos_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class oneaccess_oneos_server(SSH_Server):
    pass

class oneaccess_oneos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'oneaccess_oneos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")