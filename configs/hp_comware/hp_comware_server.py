from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from src.telnet_server.telnet_handler import Telnet_Handler
from asyncssh.process import SSHServerProcess
import time

class hp_comware_server(SSH_Server):
    pass

class hp_comware_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'hp_comware'
        super().__init__(process, options=options)
        
    def set_prompt_terminator(self, pri_terminator = ">", alt_terminator = "]") -> None:
        super().set_prompt_terminator(pri_terminator=pri_terminator, alt_terminator=alt_terminator)

class hp_comware_telnet_handler(Telnet_Handler):
    def __init__(self, reader, writer, options={}):
        super().__init__(reader, writer, options=options)
        
    def set_prompt_terminator(self, pri_terminator = ">", alt_terminator = "]") -> None:
        super().set_prompt_terminator(pri_terminator=pri_terminator, alt_terminator=alt_terminator)
        
    async def run(self):
        time.sleep(self.login_delay)

        terminator_configured = False

        try:
            await self.write("username: ")
            username = await self.read()
            await self.write("password: ")
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
                time.sleep(self.delay)
                await self.write(self.prompt_terminator)

                if not terminator_configured:                    
                    self.set_prompt_terminator()
                    
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
