from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess
import time
class sophos_sfos_server(SSH_Server):
    pass

class sophos_sfos_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'sophos_sfos'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "\\Main Menu\\ >", alt_terminator = "\\Main Menu\\ #")

    async def open(self):
        """
        Continuously reads from the process while the channel is open.
        Exits when the SSH channel is closed.
        """

        while self.process.channel._send_state == "open":
            self.process.stdout.write(self.prompt_terminator)
            command = await self.process.stdin.readline()
            self.logger.debug(f"command received `{repr(command)}`")

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
            else:
                self.respond("""
                Sophos Firmware Version SFOS 18.0.0 GA-Build339

                Main Menu

                    1.  Network  Configuration
                    2.  System   Configuration
                    3.  Route    Configuration
                    4.  Device Console
                    5.  Device Management
                    6.  VPN Management
                    7.  Shutdown/Reboot Device
                    0.  Exit

                    Select Menu Number [0-7]:
                """)

        self.process.exit(0)

        