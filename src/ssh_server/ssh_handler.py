import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from asyncssh import BreakReceived
from asyncssh.process import SSHServerProcess

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from base_handler import BaseHandler, HandlerConfig


class SSH_Handler(BaseHandler):
    """SSH Handler that inherits from BaseHandler for shared functionality."""

    def __init__(self, process: SSHServerProcess, options):
        """
        Initialize the SSH_Handler instance.

        :param process: The SSHServerProcess instance representing the SSH connection.
        :param options: Dictionary containing configuration options.
        """
        # Create config from options
        config = HandlerConfig(
            device_type=options['device_type'],
            device_version=options.get('device_version'),
            new_line=options['new_line'],
            delay=options['delay'],
            openai_support=options['openai_support'],
            openai_apikey=options['openai_apikey'],
            openai_store_responses=options.get('openai_store_responses', False),
            openai_terminal_output=options.get('openai_terminal_output'),
            openai_terminal_prompt=options.get('openai_terminal_prompt'),
        )
        super().__init__(config)

        self.process = process
        self.break_commands = ['exit', 'quit', 'logout', r'\q']

        # Password protection for enable command
        self.enable_mode = options.get('enable_mode', False)
        self.enable_secret = options.get('enable_secret', '')

        self.password_required = False
        self.password_attempts = 0
        self.max_password_attempts = 3

        # Load commands and scripts
        self._load_commands(f"{self.config_dir}/templates")
        self._load_script_function(f"{self.config_dir}/scripts", "handle_command")
            
        self.set_prompt_terminator()


    async def open(self):
        """
        Continuously reads from the process while the channel is open.
        Exits when the SSH channel is closed.
        """
        if "banner" in self.commands:
            if not self.respond(await self._get_command_output(self.commands["banner"])):
                return
        while self._is_open():
            if not self._safe_write(self.prompt_terminator):
                break
            try:
                command = await self.process.stdin.readline()
            except BreakReceived:
                self.logger.info("BreakReceived")
                if not self.respond('\x03'):
                    break
                continue
            except (ConnectionResetError, BrokenPipeError):
                self.logger.info("SSH peer disconnected while reading input")
                break
            self.logger.info(f"command received `{repr(command)}`")
            if command == "":
                # readline() returns an empty string (no newline) only at EOF,
                # i.e. the peer closed the connection. Without this guard the
                # loop spins on empty reads, pegging the CPU and starving every
                # other server in the shared event loop. A bare Enter returns a
                # newline, so it is unaffected.
                break
            command = command.strip()
            if not self._safe_write(self.get_formatted_command(command)):
                break

            if command:
                result = await self._handle_command(command)
                if not result:
                    break
                if not await self._safe_drain():
                    break

        self._safe_exit(0)

    def get_formatted_command(self, command):
        return command + '\n'
    
    def _is_open(self):
        return self.process.channel._send_state == "open"

    async def _handle_command(self, command):
        """
        Processes the given command and sends the appropriate response.

        :param command: The command string.
        """
        if self.delay:
            await asyncio.sleep(self.delay)

        if command[-1] == '?':
            self.handle_help_commands(command)
            return True

        if command in self.break_commands:
            if self.enable:
                self.enable = False
                self.set_prompt_terminator()
                return True
            return False


        # Handle script functions
        custom_script_output = self.handle_script_function(command)
        if custom_script_output:
            self.logger.info(f"custom_script_output `{custom_script_output}")

            if isinstance(custom_script_output, str):
                self.respond(custom_script_output)
            return True

        command = self.replace_command(command)
        self.logger.info(f"replaced command: `{command}`")

        # Handle custom command if applicable
        custom_command_output = self.handle_custom_command(command)
        if custom_command_output is not None:
            if custom_command_output:
                self.respond(custom_command_output)                
            return True

        # Respond with template command output if available
        if command in self.commands:
            self.respond(await self._get_command_output(self.commands[command]))
            return True
        else:
            # Sort the matching commands alphabetically
            matching_commands = self.get_matching_commands(command)
            if matching_commands:
                closest_match = matching_commands[0]  # Pick the first match
                self.respond(await self._get_command_output(self.commands[closest_match]))
                return True


        # Handle echo command
        if command.startswith('echo '):
            self.respond(command[5:])
            return True

        # Handle enable and disable command
        if self.enable_mode:
            if command == "enable" or command == "system-view" or command == "sudo":
                # Require password for enable command
                if await self.show_prompt_password():
                    self.enable = True
                    self.set_prompt_terminator()
                else:
                    # Password failed, stay in user mode
                    self.enable = False
                    self.set_prompt_terminator()
            elif command == "disable":  # disable command
                self.enable = False
                self.set_prompt_terminator()
                return True

        if self.openai_support:
            self.respond(self.get_ai_output(command))
            return True

        self.respond()
        self.logger.error(f"Command not found `{self.device_type}`: `{command}`")
        return True

    async def _get_command_output(self, file):
        """
        Reads the content of a command template file asynchronously.

        :param file: Path to the command template file.
        :return: Content of the command template file.
        """
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(
            executor, lambda: self._read_file(file)
        )

        return content

    def extract_patterns(self, pattern):
        # Split the pattern by the alternation operator '|'
        parts = pattern.split('|')

        # Remove escape characters
        cleaned_parts = [part.replace('\\', '') for part in parts]

        return cleaned_parts

    @property
    def terminator(self):
        return self.pri_terminator if self.enable or not self.enable_mode else self.alt_terminator

    async def show_prompt_password(self):
        """
        Prompts the user for enable password and validates it.
        Returns True if password is correct, False otherwise.
        """
        if self.enable_secret == "":
            return True

        self.password_required = True
        self.respond(self.prompt_password)

        # Read password input (it won't be echoed)
        password = await self.process.stdin.readline()
        password = password.strip()

        self.password_required = False

        if password == self.enable_secret:
            self.password_attempts = 0
            return True
        else:
            self.password_attempts += 1
            if self.password_attempts >= self.max_password_attempts:
                self.respond("Access denied. Too many incorrect attempts.")
                return False
            else:
                self.respond("Access denied.")
                return False

    def respond(self, response=""):
        """
        Sends a response back to the SSH client.

        :param response: The response string to send.
        """
        if not isinstance(response, (list, tuple)):
            response = [response]
        for row in response:
            self.logger.info(f"response `{row}`")
            if not self._safe_write(row + self.new_line):
                return False
        return True

    def _safe_write(self, data: str) -> bool:
        """Write to SSH output and gracefully handle peer disconnects."""
        if not self._is_open():
            return False
        try:
            self.process.stdout.write(data)
            return True
        except (ConnectionResetError, BrokenPipeError):
            self.logger.info("SSH peer disconnected while writing output")
            return False

    async def _safe_drain(self) -> bool:
        """Drain SSH output and gracefully handle peer disconnects."""
        try:
            await self.process.stdout.drain()
            return True
        except (ConnectionResetError, BrokenPipeError):
            self.logger.info("SSH peer disconnected while draining output")
            return False

    def _safe_exit(self, status: int) -> None:
        """Exit SSH process and ignore close-race errors."""
        try:
            self.process.exit(status)
        except (ConnectionResetError, BrokenPipeError):
            self.logger.info("SSH peer disconnected before exit completed")

    async def run(self):
        """
        Main entry point to run the SSH handler.
        """
        await self.open()
