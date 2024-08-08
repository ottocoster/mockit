# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/fortinet/fortinet_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class fortinet_server(SSH_Server):
    pass

class fortinet_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'fortinet'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r"#|$")


    def handle_custom_command(self, command):
        if command == "get system status | grep Version":
            return "Version: FortiOS v8.0.1"
        if command == "get system console":
            return "output : standard"
        return ""
    
        
