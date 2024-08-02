import logging
import os
import asyncssh
from asyncssh.process import SSHServerProcess
from concurrent.futures import ThreadPoolExecutor
import asyncio
import importlib

class SSH_Handler:

    def __init__(self, process: SSHServerProcess, options):
        """
        Initialize the SSH_Handler instance.

        :param process: The SSHServerProcess instance representing the SSH connection.
        :param options: Dictionary containing configuration options, such as device_type and new_line characters.
        """
        self.process = process
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device_type = options['device_type']
        self.new_line = options['new_line']
        self.enable = True
        self.break_commands = ['exit', 'quit', 'logout', '\q']
        self._load_commands(f"configs/{self.device_type}/templates")
        self.set_prompt_terminator(pattern=">#")

    async def open(self):
        """
        Continuously reads from the process while the channel is open.
        Exits when the SSH channel is closed.
        """
        while self.process.channel._send_state == "open":
            try:
                while self.process.channel._send_state == "open":
                    res = await self.read()
            except asyncssh.BreakReceived:
                self.process.exit(0)

    async def read(self):
        """
        Reads commands from the SSH channel and processes them.
        Exits when a break command is received.
        """
        while True:
            self.process.stdout.write(self.prompt_terminator)
            command = await self.process.stdin.readline()

            self.process.stdout.write(command)
            command = command.strip()

            if command in self.break_commands:
                break
            if command:
                await self._handle_command(command)

        self.process.exit(0)
      
    def handle_custom_command(self, command):
        """
        Handle custom commands not found in the template directory.
        Can be overridden in subclasses to provide specific command handling.

        :param command: The command string.
        :return: Custom command output as a string.
        """
        return ""

    async def _handle_command(self, command):
        """
        Processes the given command and sends the appropriate response.

        :param command: The command string.
        """
        self.logger.info(f"Received `{command}`")

        # Handle custom command if applicable
        custom_command_output = self.handle_custom_command(command)
        if custom_command_output:
            self.respond(custom_command_output)
            return True

        # Respond with template command output if available
        if command in self.commands:
            self.respond(await self._get_command_output(self.commands[command]))
            return True
        else:
            # Find commands that start with the given command string
            matching_commands = [cmd for cmd in self.commands if cmd.startswith(command)]
            self.logger.error(f"matching_commands `{matching_commands}`")

            if matching_commands:
                closest_match = matching_commands[0]  # Pick the first match
                self.respond(await self._get_command_output(self.commands[closest_match]))
                return True

        # Handle echo command
        if command.startswith('echo '):
            self.respond(command[5:])
            return True

        # Handle enable and disable command    
        if command == "enable" or command == "disable":
            self.enable = command == "enable"
            self.set_prompt_terminator(self.pattern)

        self.respond()
        self.logger.error(f"Command not found `{self.device_type}`: `{command}`")
        return True

    
    def _load_commands(self, template_dir):
        """
        Loads command templates from the specified directory.

        :param template_dir: Directory containing command templates.
        :return: True if commands are loaded successfully, False otherwise.
        """
        commands = {}
        if not os.path.exists(template_dir):
            self.logger.warn(f"Unable to find directory: `{template_dir}`")
            self.commands = {}
            return False
        
        for filename in os.listdir(template_dir):
            file_path = os.path.join(template_dir, filename)
            name, extension = os.path.splitext(filename)   
            if os.path.isfile(file_path) and extension == '.txt':
                commands[name] = file_path
        
        self.logger.debug(f"loaded commands: `{commands}`")
        self.commands = commands
        return True
    
    async def _get_command_output(self, file):
        """
        Reads the content of a command template file asynchronously.

        :param file: Path to the command template file.
        :return: Content of the command template file.
        """
        self.logger.debug(f"{self.device_type}: {file}")
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(
            executor, lambda: self._read_file(file)
        )
        self.logger.debug(f"command content {content}")

        return content

    def set_prompt_terminator(self, pattern = ">#"):
        """
        Sets the prompt terminator pattern for the SSH prompt.

        :param pattern: The pattern string to append to the device type.
        """
        termintator = "#"
        if not self.enable or len(pattern) < 2:
            termintator = pattern[0]
        self.pattern = pattern
        self.prompt_terminator = self.device_type + termintator + " "

    @staticmethod
    def _read_file(filename):
        """
        Reads the content of a file.

        :param filename: Path to the file.
        :return: Content of the file as a string.
        """
        with open(filename, "r") as fhand:
            return fhand.read()

    def respond(self, response = ""):
        """
        Sends a response back to the SSH client.

        :param response: The response string to send.
        """
        self.logger.debug(f"Response {response}")

        self.process.stdout.write(response + self.new_line)
