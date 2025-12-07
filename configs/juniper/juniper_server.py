from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class juniper_server(SSH_Server):
    pass

class juniper_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'juniper'
        super().__init__(process, options=options)

    def handle_custom_command(self, command):
        if command.startswith("set cli screen-width"):
            return "Screen width set to" + command.replace("terminal width", "")
        return super().handle_custom_command(command)