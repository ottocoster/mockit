import asyncio
import sys
from contextlib import suppress
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from base_handler import BaseHandler, HandlerConfig


# Telnet Handler class

class Telnet_Handler(BaseHandler):
    """Telnet Handler that inherits from BaseHandler for shared functionality."""

    prompt_username = 'Username: '
    # prompt_password inherited from BaseHandler

    def __init__(self, reader, writer, options=None):
        """
        Initialize the Telnet_Handler instance.

        :param reader: The asyncio StreamReader for reading from the connection.
        :param writer: The asyncio StreamWriter for writing to the connection.
        :param options: Dictionary containing configuration options.
        """
        if options is None:
            options = {}
        # Create config from options
        config = HandlerConfig(
            device_type=options.get('device_type', 'cisco_ios_telnet'),
            device_version=options.get('device_version'),
            new_line=options.get('new_line', '\n'),
            delay=options.get('delay', 0.025),
            openai_support=options.get('openai_support', False),
            openai_apikey=options.get('openai_apikey', ''),
        )
        super().__init__(config)

        self.reader = reader
        self.writer = writer
        self.username = options.get('username', "test")
        self.password = options.get('password', "test")
        self.login_delay = options.get('login_delay', 0.025)
        self.enable = True  # Telnet starts in enabled mode

        # Load commands and scripts
        self._load_commands(f"{self.config_dir}/templates")
        # Uncomment to enable script functions:
        # self._load_script_function(f"{self.config_dir}/scripts", "handle_command")

        self.set_prompt_terminator(pri_terminator="#", alt_terminator=">")

    async def handle_command(self, command):
        command = self.replace_command(command)

        # Handle custom command if applicable
        custom_command_output = self.handle_custom_command(command)
        if custom_command_output:
            await self.respond(custom_command_output)
            return True

        if command in self.commands:
            await self.respond(self._get_command_output(self.commands[command]))
        else:
            matching_commands = self.get_matching_commands(command)
            if matching_commands:
                closest_match = matching_commands[0]
                await self.respond(closest_match)

        if command.startswith("echo "):
            await self.respond(command[5:])
            return True

        if command in self.break_commands:
            return False

        # Handle enable and disable command
        if command == "enable" or command == "disable":
            self.enable = command == "enable"
            self.set_prompt_terminator()

        return True

    def _get_command_output(self, file):
        """Use base class _read_file method for consistency."""
        return self._read_file(file)

    async def respond(self, output=""):
        await self.write(output + self.new_line)
        self.logger.info(f"response: `{output}`")

    async def write(self, output):
        self.writer.write(output.encode())
        await self.writer.drain()

    async def read(self):
        data = await self.reader.read(1024)
        return data.decode().strip()

    async def get_credentials(self):
        await self.write(self.prompt_username)
        username = await self.read()
        await self.write(self.prompt_password)
        password = await self.read()
        return username, password

    async def run(self):
        await asyncio.sleep(self.login_delay)

        try:
            username, password = await self.get_credentials()

            if username == self.username and password == self.password:
                await self.write("Logged in successfully\n")
            else:
                await self.write("Invalid credentials!\n")
                return

            while True:
                await asyncio.sleep(self.delay)
                await self.write(self.prompt_terminator)
                command = await self.read()
                self.logger.info(f"command received `{repr(command)}`")
                await self.respond(command)
                if command:
                    result = await self.handle_command(command)
                    if not result:
                        break
        except Exception as e:
            self.logger.error(f"Error {e}")
        finally:
            self.writer.close()
            with suppress(BrokenPipeError):
                await self.writer.wait_closed()
            self.logger.info(f"Connection closed")
