import socket
import threading
import logging
import os
import importlib
from concurrent.futures import ThreadPoolExecutor
import asyncio
import sys
import time
# Telnet Handler class
class Telnet_Handler:
    def __init__(self, reader, writer, options={}):
        self.reader = reader
        self.writer = writer
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device_type = options.get('device_type', 'cisco_ios_telnet')
        self.device_version = options.get('device_version', None)
        self.username = options.get('username', "test")
        self.password = options.get('password', "test")
        self.new_line = options.get('new_line', '\n')
        self.delay = options.get('delay', 0.025)
        self.login_delay = options.get('login_delay', 0.025)
        self.pri_terminator = "#"
        self.alt_terminator = ">"
        self.enable = True
        self.config_mode = False
        self.config_pattern = "..#"
        self.break_commands = ['exit', 'quit', 'logout']
        self.handle_script_function = None
        config_dir = f"configs/{self.device_type}"
        if self.device_version:
            config_dir += f"/{self.device_version}"

        self._load_commands(f"{config_dir}/templates")
        # self._load_script_function(f"{config_dir}/scripts", "handle_command")

        self.set_prompt_terminator(pri_terminator="#", alt_terminator=">")

    def _load_script_function(self, script_path, function_name):
        module_path = script_path.replace('/', '.')
        try:
            package = importlib.import_module(module_path)
        except ModuleNotFoundError as e:
            script_dir = os.path.dirname(os.path.abspath(script_path))
            if script_dir not in sys.path:
                sys.path.append(script_dir)
            package = importlib.import_module(module_path)

        function = getattr(package, function_name, None)
        self.handle_script_function = function
        return function

    def _load_commands(self, template_dir):
        commands = {}
        if not os.path.exists(template_dir):
            self.logger.warning(f"Unable to find directory: `{template_dir}`")
            self.commands = {}
            return False

        for filename in os.listdir(template_dir):
            file_path = os.path.join(template_dir, filename)
            name, extension = os.path.splitext(filename)
            if os.path.isfile(file_path) and extension == '.txt':
                commands[name] = file_path

        # self.logger.debug(f"loaded commands: `{commands}`")
        self.commands = commands
        return True

    def set_prompt_terminator(self, pri_terminator="#", alt_terminator=">"):
        self.pri_terminator = pri_terminator
        self.alt_terminator = alt_terminator

        if self.enable:
            termintator = pri_terminator
        else:
            termintator = alt_terminator

        if self.config_mode:
            self.prompt_terminator = self.device_type + self.config_pattern + termintator + " "
        else:
            self.prompt_terminator = self.device_type + termintator + " "


    def handle_custom_command(self, command):
        """
        Handle custom commands not found in the template directory.
        Can be overridden in subclasses to provide specific command handling.

        :param command: The command string.
        :return: Custom command output as a string.
        """
        return ""
    
    def replace_command(self, command):
        command_map = {'sh': 'show', 'disp': 'display'}
        command_parts = command.split(" ")
        if command_parts[0] in command_map:
            command_parts[0] = command_map[command_parts[0]]
        return ' '.join(command_parts)

    def handle_help_commands(self, command):
        if command == "?":
            keys = sorted(self.commands.keys())
            self.respond("\n".join(keys))
            return True
        if command[-1] == '?':
            scr_command = command[:-1]
            matching_commands = self.get_matching_commands(scr_command)
            if matching_commands:
                self.respond("\n".join(matching_commands))
            return True
        return False

    def get_matching_commands(self, command):
        matching_commands = [cmd for cmd in self.commands if cmd.startswith(command)]
        self.logger.info(f"matching_commands `{matching_commands}`")
        return sorted(matching_commands) if matching_commands else None

    def respond(self, response=""):
        self.logger.debug(f"Response: {response}")
        self.conn.sendall(response.encode() + self.new_line.encode())

    async def handle_command(self, command):
        command = self.replace_command(command)
        self.logger.info(f"Processed command: `{command}`")

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
        with open(file, "r") as f:
            return f.read().strip()
        
    async def respond(self, output):
        self.logger.debug(f"Response: {output}")
        await self.write(output + self.new_line)

    async def write(self, output):
        self.writer.write(output.encode())
        await self.writer.drain()

    async def read(self):
        data = await self.reader.read(1024)
        return data.decode().strip()

    async def run(self):
        await asyncio.sleep(self.login_delay)

        try:
            await self.write("Username: ")
            username = await self.read()
            await self.write("Password: ")
            password = await self.read()

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
