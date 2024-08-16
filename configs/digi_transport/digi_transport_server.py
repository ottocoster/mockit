from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class digi_transport_server(SSH_Server):
    pass

class digi_transport_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'digi_transport'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")
    
    async def open(self):
        """
        Continuously reads from the process while the channel is open.
        Exits when the SSH channel is closed.
        """
        while self.process.channel._send_state == "open":
            self.process.stdout.write(self.prompt_terminator)
            command = await self.process.stdin.readline()
            self.logger.info(f"command received `{repr(command)}`")

            command = command.strip()

            if command:
                self.process.stdout.write(self.get_formatted_command(command))
                result = await self._handle_command(command)
                if not result:
                    break

        self.process.exit(0)