from src.ssh_server.ssh_server import SSH_Server
from src.ssh_server.ssh_handler import SSH_Handler
from asyncssh.process import SSHServerProcess

class mikrotik_routeros_server(SSH_Server):
    pass

class mikrotik_routeros_handler(SSH_Handler):
    def __init__(self, process: SSHServerProcess, options):
        options['device_type'] = 'mikrotik_routeros'
        super().__init__(process, options=options)
        if not self.device_version:
            self.device_version = "v7"
        config_dir  = f"configs/{self.device_type}/{self.device_version}"

        self._load_commands(f"{config_dir}/templates")
        self._load_script_function(f"{config_dir}/scripts", "handle_command")

    def set_prompt_terminator(self, pri_terminator = "\\] >", alt_terminator = "\\] >") -> None:
        super().set_prompt_terminator(pri_terminator=pri_terminator, alt_terminator=alt_terminator)

