import logging
import asyncssh
from ssh_server.ssh_session import create_session
from netmiko import ConnectHandler, platforms  

async def start_server(options):
    logger = logging.getLogger()
    parameters = { 
        "device_type": options["device_type"],
        "host": "localhost",
        "username": options["username"],
        "password": options["password"],
        "auto_connect": False
    }

    with ConnectHandler(**parameters) as net_connect:      
        net_connect._modify_connection_params()
        options["username"] = net_connect.username
        options["password"] = net_connect.password
        options["new_line"] = net_connect.RETURN

    logger.debug(f"Using ssh options: {options}")
    await asyncssh.create_server(
        server_factory=lambda: SSHServer(options, logger),
        host="0.0.0.0",
        port=22,
        server_host_keys=options["ssh_key"],
        process_factory=create_session,
        line_editor=len(options["echo_format"]) == 0
    )

class SSHServer(asyncssh.SSHServer):
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
