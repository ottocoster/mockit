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
    ai_support: bool = False
    ai_apikey: str = ""
    ai_url: str = ""
    """Base URL of an OpenAI-compatible API (e.g. LM Studio `http://localhost:1234/v1`).
    Empty uses the default OpenAI endpoint."""
    ai_model: str = "gpt-5.5"
    ai_store_responses: bool = False
    """Store AI-generated outputs as `<command>.txt` template files."""
    ai_terminal_output: str | None = None
    """Custom user prompt template for command outputs (AI_TERMINAL_OUTPUT).
    Supports {device_type}, {device_version} and {command} placeholders.
    Falls back to DEFAULT_AI_PROMPT when None."""
    ai_terminal_prompt: str | None = None
    """Custom system message for the AI (AI_TERMINAL_PROMPT).
    Falls back to DEFAULT_AI_SYSTEM_PROMPT."""


DEFAULT_AI_SYSTEM_PROMPT = "You are a AI vendor assistant that returns output of network devices."

DEFAULT_AI_PROMPT = """
        ### Device type
        {device_type}
        ###

        ### command
        `{command}`
        ###

        Let's assume the device type and input command are above.
        Please give me the output of this command of the device type without any explanation.
        You have to reply with only one command output.
        """


class _PromptPlaceholders(dict):
    """dict for str.format_map that leaves unknown placeholders untouched."""

    def __missing__(self, key):
        return "{" + key + "}"


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
        self.ai_support = config.ai_support
        self.ai_apikey = config.ai_apikey
        self.ai_url = config.ai_url
        self.ai_model = config.ai_model
        self.ai_store_responses = config.ai_store_responses
        self.ai_terminal_output = config.ai_terminal_output
        self.ai_terminal_prompt = config.ai_terminal_prompt

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

        # Initialize AI (OpenAI-compatible) client if enabled
        self.ai_client = None
        if self.ai_support:
            client_kwargs = {"api_key": self.ai_apikey or "lm-studio"}
            if self.ai_url:
                client_kwargs["base_url"] = self.ai_url
            self.ai_client = OpenAI(**client_kwargs)

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
        self.logger.info(f"get_ai_output called (model=`{self.ai_model}`, provider=`{self.ai_url or 'openai.com'}`)")

        prompt_template = self.ai_terminal_output if self.ai_terminal_output else DEFAULT_AI_PROMPT
        prompt = prompt_template.format_map(_PromptPlaceholders(
            device_type=self.device_type,
            device_version=self.device_version or "",
            command=command,
        ))
        system_message = self.ai_terminal_prompt or DEFAULT_AI_SYSTEM_PROMPT
        model = self.ai_model

        self.logger.debug(f"get_ai_output system prompt: `{system_message}`")
        self.logger.debug(f"get_ai_output user prompt: `{prompt}`")

        try:
            chat_completion = self.ai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                model=model,
            )
        except Exception as e:
            # AI output generation must never break the SSH/Telnet session
            # (e.g. invalid API key, network errors, rate limits, ...).
            self.logger.warning(
                f"get_ai_output failed (model=`{model}`, provider=`{self.ai_url or 'openai.com'}`): "
                f"`{type(e).__name__}: {e}`"
            )
            return ""

        message_content = chat_completion.choices[0].message.content

        self.logger.debug(f"get_ai_output raw response: `{message_content}`")

        message_content = message_content.replace("```", "").strip()

        # Store the AI output as a template file if enabled
        if self.ai_store_responses:
            self._store_ai_output(command, message_content)

        return message_content

    def _store_ai_output(self, command: str, output: str) -> bool:
        """
        Saves an AI-generated command output as a `<command>.txt` template file
        in the device's template directory, the same location commands are
        loaded from. Future invocations of the command (even in new sessions)
        are served from the template instead of the AI.

        :param command: The command name, used as the template filename.
        :param output: The AI-generated response to store.
        :return: True if the output was stored successfully, False otherwise.
        """
        command = command.strip()
        if not command:
            self.logger.warning("Not storing AI output, command is empty")
            return False

        # Reject commands containing path separators to prevent writing outside
        # the template directory
        if "/" in command or "\\" in command:
            self.logger.warning(f"Not storing AI output, invalid command name: `{command}`")
            return False

        template_dir = f"{self.config_dir}/templates"
        file_path = os.path.join(template_dir, f"{command}.txt")

        try:
            os.makedirs(template_dir, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output)
        except OSError as e:
            self.logger.warning(f"Unable to store AI output in `{file_path}`: `{e}`")
            return False

        # Make the new template available for the remainder of this session
        self.commands[command] = file_path
        self.logger.info(f"ai_output stored in `{file_path}`")
        return True

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
