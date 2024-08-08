# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/cisco_apic/cisco_apic_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class cisco_apic_server(SSH_Server):
    pass

class cisco_apic_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'cisco_apic'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=r">|#")