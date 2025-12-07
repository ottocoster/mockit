from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess


class vertiv_mph_server(SSH_Server):
    pass


class vertiv_mph_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'vertiv_mph'
        super().__init__(process, options=options)

    def set_prompt_terminator(self, pri_terminator = "cli->", alt_terminator = "cli->") -> None:
        super().set_prompt_terminator(pri_terminator=pri_terminator, alt_terminator=alt_terminator)
