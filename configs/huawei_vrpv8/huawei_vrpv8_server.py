# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/huawei_vrpv8/huawei_vrpv8_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class huawei_vrpv8_server(SSH_Server):
    pass

class huawei_vrpv8_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'huawei_vrpv8'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = ">", alt_terminator = "#")