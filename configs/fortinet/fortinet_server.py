from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class fortinet_server(SSH_Server):
    pass

class fortinet_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        self.mode = ""
        options['device_type'] = 'fortinet'
        super().__init__(process, options=options)
        
    def set_prompt_terminator(self, pri_terminator = "#", alt_terminator = "$") -> None:
        super().set_prompt_terminator(pri_terminator=pri_terminator, alt_terminator=alt_terminator)

    def handle_custom_command(self, command):
        if command == "get system status | grep Version":
            return "Version: FortiOS v8.0.1"
        if command == "get system status | grep Virtual":
            return "Virtual domain configuration: split-task"
        if command == "get system console":
            return "output : standard"
        if command == "config vdom":
            self.mode = " (vdom) "
            self.set_prompt_terminator()
            return ""
        if command == "config global":
            self.mode = " (global) "
            self.set_prompt_terminator()
            return ""
        if command == "end":
            self.mode = ""
            self.set_prompt_terminator()
            return ""
        if command.startswith("edit "):
            vdom = command[5:]
            self.mode = f" ({vdom}) "
            return f"current vf={vdom}:0"
        return super().handle_custom_command(command)
    
    def get_prompt_mode(self):
        if self.mode:
            return self.mode
        return super().get_prompt_mode() + " "
    

    
        
