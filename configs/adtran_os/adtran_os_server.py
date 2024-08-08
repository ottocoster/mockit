# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/adtran_os/adtran_os_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class adtran_os_server(SSH_Server):
    pass

class adtran_os_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'adtran_os'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")

    