# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/a10/a10_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class arista_eos_server(SSH_Server):
    pass

class arista_eos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'arista_eos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r"$|>|#")

    def handle_custom_command(self, command):
        if command == "terminal length 0":
            return "Pagination disabled"
        if command.startswith("terminal width"):
            return "Width set to" + command.replace("terminal width", "")
    