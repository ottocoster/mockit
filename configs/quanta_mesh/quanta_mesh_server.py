# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/quanta_mesh/quanta_mesh_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class quanta_mesh_server(SSH_Server):
    pass

class quanta_mesh_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'quanta_mesh'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")