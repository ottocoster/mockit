# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/ipinfusion_ocnos/ipinfusion_ocnos_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class ipinfusion_ocnos_server(SSH_Server):
    pass

class ipinfusion_ocnos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'ipinfusion_ocnos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")