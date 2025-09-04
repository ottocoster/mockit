from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class huawei_smartax_server(SSH_Server):
    pass


class huawei_smartax_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'huawei_smartax'
        super().__init__(process, options=options)
        self.enable = False
        self.config_pattern = "(config)"
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")

    async def open(self):
        self.respond("YES/NO" + self.terminator)
        await self.process.stdin.readline()
        return await super().open()
