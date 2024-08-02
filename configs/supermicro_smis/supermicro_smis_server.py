# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/supermicro_smis/supermicro_smis_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class supermicro_smis_server(SSH_Server):
    pass

class supermicro_smis_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'supermicro_smis'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")