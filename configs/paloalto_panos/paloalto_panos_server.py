# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/paloalto_panos/paloalto_panos_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class paloalto_panos_server(SSH_Server):
    pass

class paloalto_panos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'paloalto_panos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")

    def handle_custom_command(self, command):
        if command == "show admins":
            return "Client\n\n"
        return ""
    
    def get_formatted_command(self, command):
        return self.prompt_terminator + command + self.new_line