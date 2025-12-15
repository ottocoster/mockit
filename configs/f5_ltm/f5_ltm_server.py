from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class f5_ltm_server(SSH_Server):
    pass

class f5_ltm_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        self.prompt_mode = ""
        options['device_type'] = 'f5_ltm'
        super().__init__(process, options=options)
        
    def set_prompt_terminator(self, pri_terminator: str = "#", alt_terminator: str = "#") -> None:
        super().set_prompt_terminator(pri_terminator=pri_terminator, alt_terminator=alt_terminator)
    
    def handle_custom_command(self, command):
        if command == "tmsh":
            self.prompt_mode = " tmos "
            self.set_prompt_terminator()
            return "Tmsh mode enabled."
        if command == "quit":
            self.prompt_mode = ""
            self.set_prompt_terminator()
            return "Quited tmsh mode."
        return super().handle_custom_command(command)
    
    def get_prompt_mode(self):
        if self.prompt_mode:
            return self.prompt_mode
        return super().get_prompt_mode()