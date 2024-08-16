from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class supermicro_smis_server(SSH_Server):
    pass

class supermicro_smis_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'supermicro_smis'
        super().__init__(process, options=options)
        self.config_pattern = "(config-system)"
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")
        
    def handle_custom_command(self, command):
        if command == "configure terminal":
            self.config_mode = command == "configure terminal"
            self.set_prompt_terminator(pri_terminator = self.pri_terminator, alt_terminator = self.alt_terminator)
            return "Configuration successed"
        
        if command == "end" and self.config_mode:
            self.config_mode = False
            self.set_prompt_terminator(pri_terminator = self.pri_terminator, alt_terminator = self.alt_terminator)
            return "Configuration exited"

        
        if command == "set cli pagination off" or command =="terminal width 511":
            return "Configuration successed"
        return ""
    