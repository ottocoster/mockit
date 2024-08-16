from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class audiocode_66_server(SSH_Server):
    pass

class audiocode_66_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'audiocode_66'
        super().__init__(process, options=options)
        self.config_pattern = "(config-system)"
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")
        
    def handle_custom_command(self, command):
        if command == "config system":
            self.config_mode = command == "config system"
            self.set_prompt_terminator(pri_terminator = self.pri_terminator, alt_terminator = self.alt_terminator)
            return "Configuration successed"
        
        if command == "exit" and self.config_mode:
            self.config_mode = False
            self.set_prompt_terminator(pri_terminator = self.pri_terminator, alt_terminator = self.alt_terminator)
            return "Configuration exited"
        return ""
    