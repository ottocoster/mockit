from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from src.telnet_server.telnet_handler import Telnet_Handler
from asyncssh.process import SSHServerProcess

class huawei_server(SSH_Server):
    pass

class huawei_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'huawei'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "]", alt_terminator = ">")


class huawei_telnet_handler(Telnet_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'huawei'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "]", alt_terminator = ">")