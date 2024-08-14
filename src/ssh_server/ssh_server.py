import logging
import asyncssh

class SSH_Server(asyncssh.SSHServer):
    def __init__(self, options, logger):
        self.options = options
        self.logger = logger

    def connection_made(self, conn: asyncssh.SSHServerConnection):
        conn.set_extra_info(options=self.options)

    @staticmethod
    def password_auth_supported():
        return True

    def validate_password(self, username, password):
        if username != self.options["username"]:
            self.logger.error("login failed: wrong username")
            return False
        if password != self.options["password"]:
            self.logger.error("login failed: wrong password")
            return False
        return True
