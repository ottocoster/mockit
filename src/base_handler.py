"""
Base handler module providing shared functionality for SSH and Telnet handlers.

This module contains the BaseHandler abstract class that unifies common logic
between SSH_Handler and Telnet_Handler classes, eliminating code duplication.
"""

import importlib
import logging
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from openai import OpenAI


@dataclass(slots=True)
class HandlerConfig:
    """Configuration dataclass for handler initialization."""
    device_type: str
    device_version: str | None = None
    new_line: str = "\n"
    delay: float = 0.0
    pri_terminator: str = "#"
    alt_terminator: str = ">"
    openai_support: bool = False
    openai_apikey: str = ""


class BaseHandler(ABC):
    """
    Unified base class for SSH and Telnet handlers.

    This abstract class provides shared functionality including:
    - Command loading from template directories
    - Script function loading
    - AI (OpenAI) output generation
    - Command replacement/aliasing
    - Help command handling
    - Prompt terminator management
    """
    prompt_password = 'Password: '

    def __init__(self, config: HandlerConfig):
        """
        Initialize the BaseHandler instance.

        :param config: HandlerConfig instance containing configuration options.
        """
        self.logger = logging.getLogger('app')
        self.device_type = config.device_type
        self.device_version = config.device_version
        self.new_line = config.new_line
        self.delay = config.delay
        self.pri_terminator = config.pri_terminator
        self.alt_terminator = config.alt_terminator
        self.openai_support = config.openai_support
        self.openai_apikey = config.openai_apikey

        self.enable = False
        self.config_mode = False
        self.config_pattern = "..#"
        self.break_commands = ['exit', 'quit', 'logout']
        self.commands: dict[str, str] = {}
        self.handle_script_function: Callable | None = None
        self.prompt_terminator = ""

        # Build config directory path
        self.config_dir = f"configs/{self.device_type}"
        if self.device_version:
            self.config_dir += f"/{self.device_version}"

        # Initialize OpenAI client if enabled
        self.openai_client = None
        if self.openai_support:
            self.openai_client = OpenAI(api_key=self.openai_apikey)

    def _load_commands(self, template_dir: str) -> bool:
        """
        Loads command templates from the specified directory.

        :param template_dir: Directory containing command templates.
        :return: True if commands are loaded successfully, False otherwise.
        """
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

        self.commands = commands
        return True

    def _load_script_function(self, script_path: str, function_name: str) -> Callable | None:
        """
        Loads a script function from a module path.

        :param script_path: File system path to the script module.
        :param function_name: Name of the function to load.
        :return: The loaded function, or None if not found.
        """
        # Convert the file system path to a module path by replacing slashes with dots
        module_path = script_path.replace('/', '.')

        # Import the module
        try:
            package = importlib.import_module(module_path)
        except ModuleNotFoundError:
            # If the module is not found, the directory might not be in sys.path
            # Get the directory part of the script_path and add it to sys.path
            script_dir = os.path.dirname(os.path.abspath(script_path))
            if script_dir not in sys.path:
                sys.path.append(script_dir)
            # Retry importing after modifying sys.path
            try:
                package = importlib.import_module(module_path)
            except ModuleNotFoundError:
                self.logger.warning(f"Unable to load script module: `{module_path}`")
                return None

        # Access the function from the module
        function = getattr(package, function_name, None)
        self.handle_script_function = function
        return function

    def get_ai_output(self, command: str) -> str:
        """
        Generates AI-powered output for a command using OpenAI.

        :param command: The command string.
        :return: AI-generated output string.
        """
        self.logger.info("get_ai_output called")

        prompt = f"""
        ### Device type
        {self.device_type}
        ###

        ### command
        `{command}`
        ###

        Let's assume the device type and input command are above.
        Please give me the output of this command of the device type without any explanation.
        You have to reply with only one command output.
        """
        model = "gpt-4o"

        try:
            chat_completion = self.openai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a AI vendor assistant that returns output of network devices."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
            )
        except Exception as e:
            # AI output generation must never break the SSH/Telnet session
            # (e.g. invalid API key, network errors, rate limits, ...).
            self.logger.warning(f"get_ai_output failed: `{type(e).__name__}: {e}`")
            return ""

        message_content = chat_completion.choices[0].message.content
        message_content = message_content.replace("```", "").strip()

        self.logger.info(f"ai_output: `{message_content}`")
        return message_content

    def replace_command(self, command: str) -> str:
        """
        Replaces shorthand commands with their full equivalents.

        :param command: The command string.
        :return: The command with shorthand replaced.
        """
        # Define a dictionary to map shorthand to full commands
        command_map = {
            'sh': 'show',
            'disp': 'display'
        }

        # Split the command into parts
        command_parts = command.split(" ")

        # Check if the first part is a shorthand and replace it
        if command_parts[0] in command_map:
            command_parts[0] = command_map[command_parts[0]]

        # Join the command back together
        return ' '.join(command_parts)

    def handle_help_commands(self, command: str) -> bool:
        """
        Handles help commands (commands ending with '?').

        :param command: The command string.
        :return: True if this was a help command and was handled, False otherwise.
        """
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

    def get_matching_commands(self, command: str) -> list[str] | None:
        """
        Finds commands that start with the given command string.

        :param command: The command prefix to search for.
        :return: Sorted list of matching commands, or None if no matches.
        """
        matching_commands = [cmd for cmd in self.commands if cmd.startswith(command)]
        self.logger.info(f"matching_commands `{matching_commands}`")

        if matching_commands:
            return sorted(matching_commands)
        return None

    def handle_custom_command(self, command: str):
        """
        Handle custom commands not found in the template directory.
        Can be overridden in subclasses to provide specific command handling.

        :param command: The command string.
        :return: Custom command output as a string, empty string if not handled.
        """
        return None

    def set_prompt_terminator(self, pri_terminator: str = "#", alt_terminator: str = ">") -> None:
        """
        Sets the prompt terminator pattern for the prompt.

        :param pri_terminator: Primary terminator (typically for privileged mode).
        :param alt_terminator: Alternate terminator (typically for user mode).
        """
        self.pri_terminator = pri_terminator
        self.alt_terminator = alt_terminator

        self.prompt_terminator = self.device_type + self.get_prompt_mode() + self.terminator + " "

    @property
    def terminator(self):
        return self.pri_terminator if self.enable else self.alt_terminator

    def get_prompt_mode(self):
        if self.config_mode:
            return self.config_pattern
        return ""

    @staticmethod
    def _read_file(filename: str) -> str:
        """
        Reads the content of a file, stripping leading and trailing blank lines.

        :param filename: Path to the file.
        :return: Content of the file as a string.
        """
        with open(filename, "r", encoding="utf-8") as fhand:
            text = fhand.read()
            lines = text.splitlines()

            # Strip the first blank line if it exists
            if lines and lines[0].strip() == "":
                lines = lines[1:]

            # Strip the last blank line if it exists
            if lines and lines[-1].strip() == "":
                lines = lines[:-1]

            return "\n".join(lines)

    @abstractmethod
    def respond(self, response: str = "") -> None:
        """
        Sends a response back to the client.

        :param response: The response string to send.
        """
        ...

    @abstractmethod
    async def run(self) -> None:
        """
        Main entry point to run the handler.
        """
        ...
