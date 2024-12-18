from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class cisco_tp_server(SSH_Server):
    pass

class cisco_tp_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'cisco_tp'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")

    async def open(self):
        """
        Continuously reads from the process while the channel is open.
        Exits when the SSH channel is closed.
        """            
        # self.process.stdout.write("\r\nOK\r\n")

        while self.process.channel._send_state == "open":
            self.process.stdout.write(self.prompt_terminator)
            command = await self.process.stdin.readline()

            command = command.strip()
            self.process.stdout.write(self.get_formatted_command(command))
                
            self.logger.debug(f"command received `{command}`")

            if command:
                result = await self._handle_command(command)
                if not result:
                    break
            else:
                self.process.stdout.write("\r\nOK\r\n")

        self.process.exit(0)

    def handle_custom_command(self, command):
        if command == "exit":
            return "OK"
        return ""