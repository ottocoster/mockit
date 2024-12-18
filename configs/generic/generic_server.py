from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from src.telnet_server.telnet_handler import Telnet_Handler
from asyncssh.process import SSHServerProcess
import asyncio
class generic_server(SSH_Server):
    pass

class generic_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'generic'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")


class generic_telnet_handler(Telnet_Handler):
    def __init__(self, reader, writer, options={}):
        super().__init__(reader, writer, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")

    async def run(self):
        try:
            while True:
                await asyncio.sleep(self.delay)

                await self.write(self.prompt_terminator)
                command = await self.read()
                self.logger.debug(f"Command received: `{command}`")
                await self.respond(command)

                if command:
                    result = await self.handle_command(command)
                    if not result:
                        self.logger.info(f"Connection command, {command}")
                        break
        except Exception as e:
            self.logger.error(f"Error {e}")
        finally:
            self.writer.close()
            await self.writer.wait_closed()
            self.logger.info(f"Connection closed")
