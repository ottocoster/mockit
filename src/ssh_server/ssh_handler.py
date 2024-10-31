import os
from asyncssh.process import SSHServerProcess
from concurrent.futures import ThreadPoolExecutor
import asyncio
import importlib
import re
from openai import OpenAI
import logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to capture all logs, including INFO, WARNING, ERROR, and DEBUG

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
        self.device_version = options["device_version"]
        self.new_line = options['new_line']
        self.pri_terminator = "#"
        self.alt_terminator = ">"
        self.enable = True
        self.config_mode = False
        self.config_pattern = "..#"
        self.delay = options['delay']
        self.break_commands = ['exit', 'quit', 'logout', '\q']
        self.handle_script_function = None
        config_dir  = f"configs/{self.device_type}"
        if self.device_version:
            config_dir +=f"/{self.device_version}"

        self._load_commands(f"{config_dir}/templates")
        self._load_script_function(f"{config_dir}/scripts", "handle_command")

        self.set_prompt_terminator(pri_terminator="#", alt_terminator=">")

        self.openai_support = options['openai_support']
        self.openai_apikey = options['openai_apikey']
        if self.openai_support:
            self.openai_client = OpenAI(
                api_key=self.openai_apikey,
            )


    def _load_script_function(self, script_path, function_name):
        # Convert the file system path to a module path by replacing slashes with dots
        module_path = script_path.replace('/', '.')
        
        # Import the module
        try:
            package = importlib.import_module(module_path)
        except ModuleNotFoundError as e:
            # If the module is not found, the directory might not be in sys.path
            # Get the directory part of the script_path and add it to sys.path
            script_dir = os.path.dirname(os.path.abspath(script_path))
            if script_dir not in sys.path:
                sys.path.append(script_dir)
            # Retry importing after modifying sys.path
            package = importlib.import_module(module_path)
        
        # Access the function from the module
        function = getattr(package, function_name)
        
        # Assign the function to an attribute
        self.handle_script_function = function
        return function
        
    async def open(self):
        """
        Continuously reads from the process while the channel is open.
        Exits when the SSH channel is closed.
        """
        while self.process.channel._send_state == "open":
            self.process.stdout.write(self.prompt_terminator)
            command = await self.process.stdin.readline()
            self.logger.info(f"command received `{repr(command)}`")

            # Check for Ctrl+C (SIGINT)
            if command == b'\x03':  # Ctrl+C is sent as b'\x03'
                await self.handle_ctrl_c()
                continue

            command = command.strip()
            self.process.stdout.write(self.get_formatted_command(command))

            if command:
                result = await self._handle_command(command)
                if not result:
                    break

        self.process.exit(0)

    async def handle_ctrl_c(self):
        """
        Handle the Ctrl+C (SIGINT) event by resetting the prompt.
        """
        self.logger.info("Ctrl+C received, resetting prompt")
        self.respond(b'\x03')  # Move to a new line

    def get_formatted_command(self, command):
        return command + '\n'

    def handle_custom_command(self, command):
        """
        Handle custom commands not found in the template directory.
        Can be overridden in subclasses to provide specific command handling.

        :param command: The command string.
        :return: Custom command output as a string.
        """
        return ""

        
    def get_ai_output(self, command):
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

        chat_completion = self.openai_client.chat.completions.create(
            messages=[
                    {"role": "system", "content": "You are a AI vendor assistant that returns output of network devices."},
                    {"role": "user", "content": prompt}
            ],
            model=model,
        )
        message_content = chat_completion.choices[0].message.content
        message_content = message_content.replace("```", "").strip()        
        return message_content

    def replace_command(self, command: str) -> str:
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
        replaced_command = ' '.join(command_parts)
        
        return replaced_command
        
    def handle_help_commands(self, command):
        if command  == "?":
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
        # Find commands that start with the given command string
        matching_commands = [cmd for cmd in self.commands if cmd.startswith(command)]
        self.logger.info(f"matching_commands `{matching_commands}`")

        if matching_commands:
            # Sort the matching commands alphabetically
            sorted_matching_commands = sorted(matching_commands)
            return sorted_matching_commands
        return None

    async def _handle_command(self, command):
        """
        Processes the given command and sends the appropriate response.

        :param command: The command string.
        """
        self.logger.info(f"Received `{command}`")

        if self.delay:
            await asyncio.sleep(self.delay)

        if command[-1] == '?':
            self.handle_help_commands(command)
            return True

        
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

        if command in self.break_commands:
            return False

        # Handle enable and disable command    
        if command == "enable" or command == "disable":
            self.enable = command == "enable"
            self.set_prompt_terminator(pri_terminator = self.pri_terminator, alt_terminator = self.alt_terminator)

        if self.openai_support:
            self.respond(self.get_ai_output(command))
            return True

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
            self.logger.warning(f"Unable to find directory: `{template_dir}`")
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

    def extract_patterns(self, pattern):
        # Split the pattern by the alternation operator '|'
        parts = pattern.split('|')
        
        # Remove escape characters
        cleaned_parts = [part.replace('\\', '') for part in parts]
        
        return cleaned_parts
    
    def strip_first_last_blank_lines(text):
        lines = text.splitlines()

        # Strip the first blank line if it exists
        if lines and lines[0].strip() == "":
            lines = lines[1:]

        # Strip the last blank line if it exists
        if lines and lines[-1].strip() == "":
            lines = lines[:-1]

        # Join the lines back into a single string
        return "\n".join(lines)
        
    def set_prompt_terminator(self, pri_terminator = "#", alt_terminator = ">"):
        """
        Sets the prompt terminator pattern for the SSH prompt.

        :param pattern: The pattern string to append to the device type.
        """
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

    @staticmethod
    def _read_file(filename):
        """
        Reads the content of a file.

        :param filename: Path to the file.
        :return: Content of the file as a string.
        """
        with open(filename, "r") as fhand:
            text = fhand.read()
            lines = text.splitlines()

            # Strip the first blank line if it exists
            if lines and lines[0].strip() == "":
                lines = lines[1:]

            # Strip the last blank line if it exists
            if lines and lines[-1].strip() == "":
                lines = lines[:-1]

            # Join the lines back into a single string
            return "\n".join(lines)

    def respond(self, response = ""):
        """
        Sends a response back to the SSH client.

        :param response: The response string to send.
        """
        self.logger.debug(f"Response {response}")
        self.process.stdout.write(response + self.new_line)
