"""
Browser runtime for Mock'it.

Runs the unmodified device handlers from `src/` and `configs/` inside Pyodide
(CPython compiled to WebAssembly). A browser tab cannot listen on TCP ports, so
there is no SSH/Telnet/SNMP server here: instead this module stands in for the
asyncssh `SSHServerProcess` that a real SSH session would hand to the device
handler, and wires its stdin/stdout to an xterm.js terminal in the page.

Everything above the transport (prompts, templates, scripts, enable mode,
help `?`, command aliases, per-device overrides) is the real Mock'it code.
"""

import asyncio
import importlib
import logging
import os
import sys
import types

# ---------------------------------------------------------------------------
# Stubs for modules that cannot run in the browser
# ---------------------------------------------------------------------------

def _install_stubs():
    # asyncssh: only the names the handler modules import are needed.
    asyncssh = types.ModuleType("asyncssh")

    class BreakReceived(Exception):
        pass

    class SSHServer:
        def __init__(self, *args, **kwargs):
            pass

    asyncssh.BreakReceived = BreakReceived
    asyncssh.SSHServer = SSHServer
    asyncssh.SSHServerConnection = object
    process_mod = types.ModuleType("asyncssh.process")
    process_mod.SSHServerProcess = object
    asyncssh.process = process_mod
    sys.modules["asyncssh"] = asyncssh
    sys.modules["asyncssh.process"] = process_mod

    # openai: AI mode is not supported in the browser build.
    openai = types.ModuleType("openai")

    class OpenAI:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("AI support is not available in the browser build")

    openai.OpenAI = OpenAI
    sys.modules["openai"] = openai

    # sqlite3 is not part of Pyodide's core stdlib. Device scripts only use the
    # small key/value API in db_operations, so back it with an in-memory dict.
    db = types.ModuleType("src.ssh_server.db_operations")
    tables: dict[str, dict[str, str]] = {}

    def create_table(device_type):
        tables.setdefault(device_type, {})

    def create_record(device_type, key, value):
        table = tables.setdefault(device_type, {})
        if key in table:
            raise ValueError(f"UNIQUE constraint failed: {device_type}.key")
        table[key] = value

    def read_record(device_type, key):
        return tables.get(device_type, {}).get(key)

    def read_records(device_type, key):
        value = read_record(device_type, key)
        return [value] if value is not None else None

    def update_record(device_type, key, new_value):
        table = tables.setdefault(device_type, {})
        if key in table:
            table[key] = new_value

    def delete_record(device_type, key):
        tables.get(device_type, {}).pop(key, None)

    for fn in (create_table, create_record, read_record, read_records, update_record, delete_record):
        setattr(db, fn.__name__, fn)
    db.DB_PATH = ":memory:"
    sys.modules["src.ssh_server.db_operations"] = db


_install_stubs()

# The device modules import `src.ssh_server.ssh_handler`; the handler itself
# imports `base_handler` as a top-level module, exactly like in the container.
for path in ("/mockit", "/mockit/src"):
    if path not in sys.path:
        sys.path.insert(0, path)
os.chdir("/mockit")

logging.basicConfig(level=logging.WARNING)

from src.ssh_server.ssh_handler import SSH_Handler  # noqa: E402


async def _read_template(self, file):
    # The container version reads templates through a ThreadPoolExecutor;
    # Pyodide has no threads, so read synchronously.
    return self._read_file(file)


SSH_Handler._get_command_output = _read_template


# ---------------------------------------------------------------------------
# Fake SSH process
# ---------------------------------------------------------------------------

class _Stdin:
    def __init__(self):
        self.queue: asyncio.Queue[str] = asyncio.Queue()

    async def readline(self) -> str:
        return await self.queue.get()


class _Stdout:
    def __init__(self, write):
        self._write = write

    def write(self, data: str):
        # xterm.js needs CRLF to return the cursor to column 0.
        self._write(data.replace("\r\n", "\n").replace("\n", "\r\n"))

    async def drain(self):
        await asyncio.sleep(0)


class _Channel:
    _send_state = "open"


class BrowserProcess:
    """Mimics the parts of asyncssh.SSHServerProcess the handlers touch."""

    def __init__(self, write, on_exit):
        self.stdin = _Stdin()
        self.stdout = _Stdout(write)
        self.stderr = self.stdout
        self.channel = _Channel()
        self._on_exit = on_exit
        self.exit_status = None

    def get_extra_info(self, name, default=None):
        if name == "peername":
            return ("browser", 0)
        return default

    def exit(self, status: int):
        if self.channel._send_state == "open":
            self.channel._send_state = "closed"
            self.exit_status = status
            self._on_exit(status)


# ---------------------------------------------------------------------------
# Device discovery / loading (mirrors src/start_ssh.py, minus netmiko)
# ---------------------------------------------------------------------------

def list_devices() -> list[dict]:
    """Return every device type (and version) that has an SSH handler."""
    devices = []
    for device_type in sorted(os.listdir("configs")):
        base = f"configs/{device_type}"
        if not os.path.isdir(base):
            continue
        if os.path.isfile(f"{base}/{device_type}_server.py"):
            devices.append({"type": device_type, "version": ""})
        for version in sorted(os.listdir(base)):
            if os.path.isfile(f"{base}/{version}/{device_type}_{version}_server.py"):
                devices.append({"type": device_type, "version": version})
    return devices


def load_handler_class(device_type: str, device_version: str = ""):
    if device_version:
        mod = f"configs.{device_type}.{device_version}.{device_type}_{device_version}_server"
    else:
        mod = f"configs.{device_type}.{device_type}_server"
    module = importlib.import_module(mod)
    return getattr(module, f"{device_type}_handler")


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

LOGIN_USERNAME = "root"
LOGIN_PASSWORD = "Welcome01!"


class Session:
    def __init__(self, device_type, device_version, write, on_exit, enable_secret=""):
        self.process = BrowserProcess(write, on_exit)
        handler_class = load_handler_class(device_type, device_version)
        options = {
            "device_type": device_type,
            "device_version": device_version or None,
            "new_line": "\n",
            "delay": 0,
            "ai_support": False,
            "ai_apikey": "",
            "honeypot_mode": False,
            "enable_mode": bool(enable_secret),
            "enable_secret": enable_secret,
            # Only used by the few handlers that run their own login prompt
            # inside the session (e.g. cisco_s200); same defaults as the image.
            "username": LOGIN_USERNAME,
            "password": LOGIN_PASSWORD,
            "login_delay": 0,
            "login_retry": 0,
        }
        self.handler = handler_class(self.process, options)
        self.task = asyncio.ensure_future(self._run())

    async def _run(self):
        try:
            await self.handler.run()
        except Exception as e:  # surface crashes in the terminal
            self.process.stdout.write(f"\n[mockit] handler error: {type(e).__name__}: {e}\n")
            self.process.exit(1)

    def send_line(self, line: str):
        self.process.stdin.queue.put_nowait(line + "\n")

    def send_break(self):
        self.process.stdin.queue.put_nowait("\x03\n")

    def password_mode(self) -> bool:
        return bool(getattr(self.handler, "password_required", False))

    def complete(self, prefix: str) -> list[str]:
        return self.handler.get_matching_commands(prefix) or []

    def close(self):
        self.process.exit(0)
        self.task.cancel()


def new_session(device_type, device_version, write, on_exit, enable_secret=""):
    return Session(device_type, device_version, write, on_exit, enable_secret)
