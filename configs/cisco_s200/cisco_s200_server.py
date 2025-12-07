from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class cisco_s200_server(SSH_Server):
    def __init__(self, options, logger):
        super().__init__(options, logger)

        self.username = None
        self.password = None        
    
    def begin_auth(self, username):
        self.username = username
        print(f"Login as: {username}")
        return False  # Return True to indicate that authentication is required


class cisco_s200_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'cisco_s200'
        super().__init__(process, options=options)
        self.logged_in = False
        self.username = options['username']
        self.password = options['password']

    async def open(self):
        """
        Continuously reads from the process while the channel is open.
        Exits when the SSH channel is closed.
        """
        username = ""
        password = ""
        while self.process.channel._send_state == "open":
            if self.logged_in:
                self.process.stdout.write(self.prompt_terminator)
            else:
                if not username:
                    self.process.stdout.write("login as:")

            command = await self.process.stdin.readline()

            command = command.strip()

            self.logger.debug(f"command {command}")
            if not self.logged_in:
                if not command:
                    continue
                if not username:
                    username = command
                    self.process.stdout.write("Password:")
                else:
                    password = command
                    self.logger.debug(f"username: {username}, password: {password}")
                    self.logger.debug(f"self.username: {self.username}, self.password: {self.password}")

                    if username == self.username and password == self.password:
                        self.logged_in = True
                        self.logger.info(f"Authentication passed.")
                        self.respond()
                    else:
                        self.logger.info(f"Authentication failed.")
                        self.respond("Authentication failed.")
                        break
            else:
                if command:
                    self.process.stdout.write(self.prompt_terminator + command + self.new_line)
                self.logger.debug(f"command received `{command}`")

                if command:
                    result = await self._handle_command(command)
                    if not result:
                        break

        self.process.exit(0)    