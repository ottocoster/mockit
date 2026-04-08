from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from src.telnet_server.telnet_handler import Telnet_Handler

from asyncssh.process import SSHServerProcess

class audiocode_66_server(SSH_Server):
    pass

class audiocode_66_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'audiocode_66'
        super().__init__(process, options=options)
        self.config_pattern = "(config-system)"
        
    def handle_custom_command(self, command):
        if command == "config system":
            self.config_mode = command == "config system"
            self.set_prompt_terminator()
            return "Configuration successed"
        
        if command == "exit" and self.config_mode:
            self.config_mode = False
            self.set_prompt_terminator()
            return "Configuration exited", self.terminator
        return super().handle_custom_command(command)


class audiocode_66_telnet_handler(Telnet_Handler):
    def __init__(self, reader, writer, options={}):
        super().__init__(reader, writer, options=options)
        self.config_pattern = "(config-system)"
        
    def handle_custom_command(self, command):
        if command == "config system":
            self.config_mode = command == "config system"
            self.set_prompt_terminator()
            return "Configuration successed"
        
        if command == "exit" and self.config_mode:
            self.config_mode = False
            self.set_prompt_terminator()
            return "Configuration exited", self.terminator
        return super().handle_custom_command(command)