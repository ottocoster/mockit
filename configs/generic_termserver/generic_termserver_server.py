from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from src.telnet_server.telnet_handler import Telnet_Handler
from asyncssh.process import SSHServerProcess
import time
class generic_termserver_server(SSH_Server):
    pass

class generic_termserver_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'generic_termserver'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")


class generic_termserver_telnet_handler(Telnet_Handler):
    def __init__(self, reader, writer, options={}):
        super().__init__(reader, writer, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")

    def run(self):
        try:
            while True:
                time.sleep(self.delay)

                self.write(self.prompt_terminator)
                command = self.conn.recv(1024).decode().strip()
                self.logger.debug(f"Command received: `{command}`")
                self.respond(command)

                if command:
                    result = self.handle_command(command)
                    if not result:
                        self.logger.debug(f"Connection command, {command}")
                        break
        except Exception as e:
            self.logger.error(f"Error {e}")
        finally:
            self.conn.close()
            self.logger.info(f"Connection closed")
