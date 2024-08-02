# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/huawei_vrp/huawei_vrp_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class huawei_vrp_server(SSH_Server):
    pass

class huawei_vrp_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'huawei_vrp'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")