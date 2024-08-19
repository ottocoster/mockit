import asyncssh
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict

connection_attempts = defaultdict(list)  # Store connection attempts with timestamps

class SSH_Server(asyncssh.SSHServer):
    def __init__(self, options, logger):
        """
        Initialize the SSH_Server instance.

        :param options: Dictionary containing configuration options, such as username and password.
        :param logger: Logger instance for logging messages.
        """
        self.options = options
        self.login_delay = options["login_delay"]
        self.login_retry = options["login_retry"]
        self.logger = logger

    def connection_made(self, conn: asyncssh.SSHServerConnection):
        global connection_attempts
        """
        Called when a new SSH connection is made.

        :param conn: The SSHServerConnection instance representing the connection.
        """
        ip_address = conn.get_extra_info('peername')[0]  # Get the IP address of the client
        current_time = datetime.now()

        # Remove attempts older than 1 minute
        connection_attempts[ip_address] = [
            t for t in connection_attempts[ip_address] 
            if current_time - t < timedelta(minutes=1)
        ]
        # Add the current attempt
        connection_attempts[ip_address].append(current_time)

        if len(connection_attempts[ip_address]) <= self.login_retry:
            self.logger.error(f"Connection attempt {len(connection_attempts[ip_address])} from {ip_address} rejected.")
            conn.close()  # Close the connection
            return
        else:
            self.logger.info(f"Connection attempt {len(connection_attempts[ip_address])} from {ip_address} accepted.")
            conn.set_extra_info(options=self.options)
            super().connection_made(conn)  # Call the superclass method

    @staticmethod
    def password_auth_supported():
        """
        Indicate that password authentication is supported.

        :return: True, indicating password authentication is supported.
        """
        return True

    async def validate_password(self, username, password):
        """
        Validate the username and password provided by the client.

        :param username: The username provided by the client.
        :param password: The password provided by the client.
        :return: True if the username and password are valid, False otherwise.
        """
        await asyncio.sleep(self.login_delay)

        if username != self.options["username"]:
            self.logger.error("login failed: wrong username")
            return False
        if password != self.options["password"]:
            self.logger.error("login failed: wrong password")
            return False
        return True
