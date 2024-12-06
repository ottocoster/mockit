from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from src.telnet_server.telnet_handler import Telnet_Handler
from asyncssh.process import SSHServerProcess
import asyncio

class tplink_jetstream_server(SSH_Server):
    pass

class tplink_jetstream_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'tplink_jetstream'
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
            self.logger.debug(f"command received `{repr(command)}`")

            command = command.strip()
                
            if command:
                self.process.stdout.write(self.get_formatted_command(command))
                result = await self._handle_command(command)
                if not result:
                    break

        self.process.exit(0)


class tplink_jetstream_telnet_handler(Telnet_Handler):
    def __init__(self, reader, writer, options={}):
        super().__init__(reader, writer, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")

    async def run(self):
        await asyncio.sleep(self.login_delay)

        try:
            await self.write("User: ")
            username = await self.read()
            await self.write("Password: ")
            password = await self.read()
            self.logger.debug(f"username: `{self.username}`")
            self.logger.debug(f"password: `{self.password}`")
            self.logger.debug(f"username received: `{username}`")
            self.logger.debug(f"password received: `{password}`")

            if username == self.username and password == self.password:
                await self.write("Logged in successfully\n")
            else:
                await self.write("Invalid credentials!\n")
                return

            while True:
                await asyncio.sleep(self.delay)

                await self.write(self.prompt_terminator)
                command = await self.read()
                self.logger.debug(f"Command received: `{command}`")
                await self.respond(command)

                if command:
                    result = await self.handle_command(command)
                    if not result:
                        break
        except Exception as e:
            self.logger.error(f"Error {e}")
        finally:
            self.writer.close()
            await self.writer.wait_closed()
            self.logger.info(f"Connection closed")
