# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/ubiquiti_edge/ubiquiti_edge_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class ubiquiti_edge_server(SSH_Server):
    pass

class ubiquiti_edge_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'ubiquiti_edge'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")