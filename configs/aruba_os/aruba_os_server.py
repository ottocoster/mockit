from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class aruba_os_server(SSH_Server):
    pass

class aruba_os_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'aruba_os'
        super().__init__(process, options=options)
        
    def set_prompt_terminator(self, pri_terminator: str = "#", alt_terminator: str = "#") -> None:
        super().set_prompt_terminator(pri_terminator=pri_terminator, alt_terminator=alt_terminator)

    