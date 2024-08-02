# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/audiocode_shell/audiocode_shell_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class audiocode_shell_server(SSH_Server):
    pass

class audiocode_shell_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'audiocode_shell'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")