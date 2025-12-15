from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class nec_ix_server(SSH_Server):
    pass

class nec_ix_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'nec_ix'
        super().__init__(process, options=options)
        self.config_pattern = "(config)"

    def handle_custom_command(self, command):
        if "svintr-config" in command:
            self.config_mode = True
            self.set_prompt_terminator()
            return "Enable mode"
        if "exit" in command:
            self.config_mode = False
            self.set_prompt_terminator()
            return "Exit mode"
        return super().handle_custom_command(command)