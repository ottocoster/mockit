# from ssh_server.ssh_server import SSH_Server
# from ssh_server.ssh_handler import SSH_Handler
# configs/tplink_jetstream/tplink_jetstream_server.py
from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class tplink_jetstream_server(SSH_Server):
    pass

class tplink_jetstream_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'tplink_jetstream'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pattern=">#")