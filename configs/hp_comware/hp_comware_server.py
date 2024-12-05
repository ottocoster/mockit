from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from src.telnet_server.telnet_handler import Telnet_Handler
from asyncssh.process import SSHServerProcess
import time

class hp_comware_server(SSH_Server):
    pass

class hp_comware_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'hp_comware'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "]", alt_terminator = ">")

class hp_comware_telnet_handler(Telnet_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'hp_comware'
        super().__init__(process, options=options)
        self.set_prompt_terminator(pri_terminator = "#", alt_terminator = ">")



    def run(self):
        time.sleep(self.login_delay)

        terminator_configured = False

        try:
            self.write("username: ")
            username = self.read()
            self.write("password: ")
            password = self.read()
            self.logger.debug(f"username: `{self.username}`")
            self.logger.debug(f"password: `{self.password}`")
            self.logger.debug(f"username received: `{username}`")
            self.logger.debug(f"password received: `{password}`")

            if username == self.username and password == self.password:
                self.write("Logged in successfully\n")
            else:
                self.write("Invalid credentials!\n")
                return

            while True:
                time.sleep(self.delay)
                self.write(self.prompt_terminator)

                if not terminator_configured:
                    self.set_prompt_terminator(pri_terminator = "]", alt_terminator = ">")
                    
                command = self.conn.recv(1024).decode().strip()
                self.logger.debug(f"Command received: `{command}`")
                self.respond(command)

                if command:
                    result = self.handle_command(command)
                    if not result:
                        break
        except Exception as e:
            self.logger.error(f"Error {e}")
        finally:
            self.conn.close()
            self.logger.info(f"Connection closed")
