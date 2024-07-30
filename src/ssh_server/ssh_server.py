import logging
import asyncssh

class SSH_Server(asyncssh.SSHServer):
    def __init__(self, options, logger):
        """
        Initialize the SSH_Server instance.

        :param options: Dictionary containing configuration options, such as username and password.
        :param logger: Logger instance for logging messages.
        """
        self.options = options
        self.logger = logger

    def connection_made(self, conn: asyncssh.SSHServerConnection):
        """
        Called when a new SSH connection is made.

        :param conn: The SSHServerConnection instance representing the connection.
        """
        conn.set_extra_info(options=self.options)

    @staticmethod
    def password_auth_supported():
        """
        Indicate that password authentication is supported.

        :return: True, indicating password authentication is supported.
        """
        return True

    def validate_password(self, username, password):
        """
        Validate the username and password provided by the client.

        :param username: The username provided by the client.
        :param password: The password provided by the client.
        :return: True if the username and password are valid, False otherwise.
        """
        if username != self.options["username"]:
            self.logger.error("login failed: wrong username")
            return False
        if password != self.options["password"]:
            self.logger.error("login failed: wrong password")
            return False
        return True
