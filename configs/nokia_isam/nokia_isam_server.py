from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class nokia_isam_server(SSH_Server):
    pass

class nokia_isam_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        self.mode = ""
        options['device_type'] = 'nokia_isam'
        super().__init__(process, options=options)
        
    def handle_custom_command(self, command):
        if command.startswith("environment"):
            self.mode += ">environment"
            self.set_prompt_terminator()
            return ""
        if command.startswith("configure"):
            self.mode += ">configure"
            self.set_prompt_terminator()
            return ""
        if command.startswith("system"):
            self.mode += ">system"
            self.set_prompt_terminator()
            return ""
        if command == "exit":
            if self.mode:
                self.mode = self.mode.rsplit('>', 1)[0]
                self.set_prompt_terminator()
            return ""
        if command == "exit all":
            self.mode = ""
            self.set_prompt_terminator()
            return ""
        return super().handle_custom_command(command)
    
    def get_prompt_mode(self):
        if self.mode:
            return self.mode
        return super().get_prompt_mode()
    

    
        
