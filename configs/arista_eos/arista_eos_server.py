from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess
from src.telnet_server.telnet_handler import Telnet_Handler

class arista_eos_server(SSH_Server):
    pass

class arista_eos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'arista_eos'
        super().__init__(process, options=options)

    def handle_custom_command(self, command):
        if command == "terminal length 0":
            return "Pagination disabled"
        if command.startswith("terminal width"):
            return "Width set to" + command.replace("terminal width", "")
        return super().handle_custom_command(command)
    

class arista_eos_telnet_handler(Telnet_Handler):
    def __init__(self, reader, writer, options={}):
        super().__init__(reader, writer, options=options)

    def handle_custom_command(self, command):
        if command == "terminal length 0":
            return "Pagination disabled"
        if command.startswith("terminal width"):
            return "Width set to" + command.replace("terminal width", "")
        return super().handle_custom_command(command)
    