from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from src.telnet_server.telnet_handler import Telnet_Handler

from asyncssh.process import SSHServerProcess

huawei_olt_server = SSH_Server


class huawei_olt_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'huawei_olt'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")
    
    def handle_custom_command(self, command):
        if command == "huawei_olt":
            return "huawei_olt"


class huawei_olt_telnet_handler(Telnet_Handler):
    def __init__(self, reader, writer, options=None):
        super().__init__(reader, writer, options=options or {})
        self.set_prompt_terminator(pri_terminator = ">", alt_terminator = "$")

    def handle_custom_command(self, command):
        if command == "huawei_olt":
            return "huawei_olt"

    async def open(self):
        self.respond("YES/NO" + self.terminator)
        await self.process.stdin.readline()
        return await super().open()