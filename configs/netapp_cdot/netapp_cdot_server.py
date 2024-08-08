# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/netapp_cdot/netapp_cdot_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class netapp_cdot_server(SSH_Server):
    pass

class netapp_cdot_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'netapp_cdot'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")