from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from src.telnet_server.telnet_handler import Telnet_Handler

from asyncssh.process import SSHServerProcess

class oedgecore_sonic_server(SSH_Server):
    pass

class edgecore_sonic_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'edgecore_sonic'
        super().__init__(process, options=options)



class edgecore_sonic_telnet_handler(Telnet_Handler):
    def __init__(self, reader, writer, options={}):
        super().__init__(reader, writer, options=options)


    def handle_custom_command(self, command):
        if command.startswith("screen-width"):
            return self.prompt_terminator + "\n\n"
        return super().handle_custom_command(command)
    
