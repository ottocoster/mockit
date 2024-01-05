import logging
import os
import asyncssh
from asyncssh.process import SSHServerProcess
from concurrent.futures import ThreadPoolExecutor
import asyncio
import importlib

async def create_session(process: SSHServerProcess):
    session = SSHSession(process, process.get_extra_info("options"))
    await session.open()

class SSHSession:

    def __init__(self, process: SSHServerProcess, options):
        self.options = options
        self.process = process
        self.logger = logging.getLogger(self.__class__.__name__)

        config_dir = f"/configs/{options['device_type']}"
        version = options["device_version"]
        if version:
            config_dir += f"/{version}"
        self.module = importlib.import_module(f'{config_dir}/scripts'.replace('/', '.')[1:])
        self.commands = self._load_commands(f'{config_dir}/templates')

    async def open(self):        
        while self.process.channel._send_state == "open":
            try:
                while self.process.channel._send_state == "open":
                    res = await self.read()
            except asyncssh.BreakReceived:
                self.new_line()

    async def read(self):
        self.new_line()
        self.send_initial_prompt()
        while True:
            user_input = await self.process.stdin.readline()
            if user_input == "":
                break
            res = await self._handle_command(user_input.rstrip())
            if not res:
                break
        self.process.exit(0)

    async def _handle_command(self, command):
        if not command:
            self.send_initial_prompt()
            return True

        if await self.module.handle_command(command, self):
            return True

        if command in self.commands:
            self.respond(await self._execute_command(self.commands[command]))
            return True

        if command == "exit" or command == "quit" or command == "logout":
            return False

        if command.startswith('echo '):
            self.respond(command[5:])
            return True

        self.logger.error(f"Command not found `{self.options['device_type']}`: `{command}`")
        self.send_prompt()
        return True

    def _load_commands(self, config_dir):
        if not os.path.exists(config_dir):
            self.logger.warn(f"Unable to find directory: `{config_dir}`")
        commands = {}
        for filename in os.listdir(config_dir):
            file_path = os.path.join(config_dir, filename)
            name, extension = os.path.splitext(filename)   
            if os.path.isfile(file_path) and extension == '.txt':
                commands[name] = file_path
        return commands
    
    async def _execute_command(self, file):
        self.logger.debug(f"{self.options['device_type']}: {file}")
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(
            executor, lambda: self._read_file(file)
        )
        return self.options["new_line"].join(content.splitlines())

    @staticmethod
    def _read_file(filename):
        with open(filename, "r") as fhand:
            return fhand.read()
    
    def new_line(self):
        self.process.stdout.write(self.options["new_line"])

    def respond(self, response):
        self.logger.debug(response)
        self.process.stdout.write(response + self.options["new_line"])
        self.send_prompt()

    def send_initial_prompt(self):
        self.process.stdout.write(self.options["device_type"] + self.options["prompt"])

    def send_prompt(self):
        self.process.stdout.write(self.options["device_type"] + self.options["prompt_command"])
