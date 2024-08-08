# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/mellanox_mlnxos/mellanox_mlnxos_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class mellanox_mlnxos_server(SSH_Server):
    pass

class mellanox_mlnxos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'mellanox_mlnxos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r"#")