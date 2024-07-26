import logging
import os
import asyncssh
from asyncssh.process import SSHServerProcess
from concurrent.futures import ThreadPoolExecutor
import asyncio
import importlib

class SSH_Handler:

    def __init__(self, process: SSHServerProcess, options):
        self.process = process
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device_type = options['device_type']
        self.new_line = options['new_line']
        self.break_commands = ['exit', 'quit', 'logout', '\q' ]
        self._load_commands(f"configs/{self.device_type}/templates")
        self.set_prompt_terminator(pattern="#")
        self.response_format = "<response><new_line>"

    async def open(self):
        while self.process.channel._send_state == "open":
            try:
                while self.process.channel._send_state == "open":
                    res = await self.read()
            except asyncssh.BreakReceived:
                self.process.exit(0)

    async def read(self):
        while True:
            self.process.stdout.write(self.prompt_terminator)
            command = await self.process.stdin.readline()
            command = command.strip()

            if command in self.break_commands:
                break
            if command:
                await self._handle_command(command)

        self.process.exit(0)
        # self.new_line()
        # self.send_prompt()
        # while True:
        #     user_input = await self.process.stdin.readline()
        #     if user_input == "":
        #         break
        #     res = await self._handle_command(user_input.rstrip())
        #     if not res:
        #         break
        # self.process.exit(0)

       

    def handle_custom_command(self, command):
        return ""

    async def _handle_command(self, command):
        self.logger.info(f"Received `{command}`")

        custom_command_output = self.handle_custom_command(command)
        if custom_command_output:
            self.respond(custom_command_output)
            return True

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

        if command.startswith('echo '):
            self.respond(command[5:])
            return True

        self.logger.error(f"Command not found `{self.device_type}`: `{command}`")
        # self.send_command_prompt()
        return True

    def _load_commands(self, template_dir):
        if not os.path.exists(template_dir):
            self.logger.warn(f"Unable to find directory: `{template_dir}`")
        commands = {}
        for filename in os.listdir(template_dir):
            file_path = os.path.join(template_dir, filename)
            name, extension = os.path.splitext(filename)   
            if os.path.isfile(file_path) and extension == '.txt':
                commands[name] = file_path
        self.logger.debug(f"loaded commands: `{commands}`")
        self.commands = commands
        return True
    
    async def _get_command_output(self, file):
        self.logger.debug(f"{self.device_type}: {file}")
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(
            executor, lambda: self._read_file(file)
        )
        self.logger.debug(f"command content {content}")

        return content

    def set_prompt_terminator(self, pattern):
        self.prompt_terminator = self.device_type + pattern

    @staticmethod
    def _read_file(filename):
        with open(filename, "r") as fhand:
            return fhand.read()
    
    # def set_prompt(self, prompt):
    #     self.options['temp_prompt'] = prompt
    
    # def new_line(self):
    #     self.process.stdout.write(self.options["new_line"])

    def respond(self, response = ""):
        self.process.stdout.write(response + self.new_line)
        # self.send_command_prompt()

    # def format_text(self, format: str, response = ""):
    #     prompt = self.options['prompt']
    #     if 'temp_prompt' in self.options:
    #         prompt = self.options['temp_prompt']
    #     return format.replace('<response>', response).replace('<new_line>', self.options['new_line']).replace('<device_type>', self.options['device_type']).replace('<prompt>', prompt)

    # def send_prompt(self):
    #     self.process.stdout.write(self.format_text(self.options['default_prompt_format']))

    # def send_command_prompt(self):
    #     self.process.stdout.write(self.format_text(self.options['command_prompt_format']))