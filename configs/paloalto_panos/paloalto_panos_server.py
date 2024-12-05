from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from src.telnet_server.telnet_handler import Telnet_Handler

from asyncssh.process import SSHServerProcess
import asyncio

class paloalto_panos_server(SSH_Server):
    pass

class paloalto_panos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'paloalto_panos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")

    def handle_custom_command(self, command):
        if command == "show admins":
            return "Client\n\n"
        return ""
    
    def get_formatted_command(self, command):
        return self.prompt_terminator + command + self.new_line


class paloalto_panos_telnet_handler(Telnet_Handler):
    def __init__(self, reader, writer, options={}):
        super().__init__(reader, writer, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")
        self.new_line = '\r\n'

    def handle_custom_command(self, command):
        if command == "show admins":
            return "Client"
        
        if command == "set cli scripting-mode on":
            return self.prompt_terminator + "mode on"

        if command == "set cli terminal width 500":
            return "set cli terminal width 500\n"

        if command == "set cli pager off":
            return "set cli pager off"

        return ""
    

    async def run(self):
        await asyncio.sleep(self.login_delay)

        try:
            await self.write("Username: ")
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
                else:
                    await self.respond("")
        except Exception as e:
            self.logger.error(f"Error {e}")
        finally:
            self.writer.close()
            await self.writer.wait_closed()
            self.logger.info(f"Connection closed")
