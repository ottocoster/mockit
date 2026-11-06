"""
Honeypot logging helper.

When HONEYPOT_MODE=true, SSH/Telnet sessions accept any credentials and
every login attempt plus all subsequent input is recorded in txt files:

    <HONEYPOT_LOG_DIR>/<yyyy-mm-dd>/<ip>.txt

One folder per day, one file per attacking IP, so brute-force floods stay
grouped and old days can be archived/removed as a folder.
"""
import logging
import os
import re
from datetime import datetime

# Folder the honeypot logs live in. Relative paths resolve to the working
# directory. The container default is /logs (mapped through docker-compose);
# /logs is used automatically when it exists (container), otherwise ./logs.
_DEFAULT_LOG_DIR = "/logs" if os.path.isdir("/logs") else "logs"
HONEYPOT_LOG_DIR = os.environ.get("HONEYPOT_LOG_DIR", _DEFAULT_LOG_DIR)


def _safe_filename(ip: str) -> str:
    """
    Turn the peer IP (or 'unknown') into a safe file name for any OS.
    """
    cleaned = re.sub(r'[^\w.\-]+', '_', (ip or "").strip())
    return cleaned or "unknown"


def log(ip: str, event: str) -> None:
    """
    Append a timestamped line to the honeypot log file of the given IP.

    Creates <HONEYPOT_LOG_DIR>/<yyyy-mm-dd>/ on first use, then appends to
    <ip>.txt inside it. Any other events from the same IP/file during the
    same day (from SSH, Telnet or other tasks) are appended sequentially.

    :param ip: Peer IP the event came from (selects the file).
    :param event: The event text without timestamp.
    """
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {event}\n"
    try:
        directory = os.path.join(
            HONEYPOT_LOG_DIR, datetime.now().strftime("%Y-%m-%d"))
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, f"{_safe_filename(ip)}.txt")
        with open(path, "a", encoding="utf-8", errors="replace") as f:
            f.write(line)
    except OSError as e:
        # Recording must never break the session.
        logging.getLogger('app').error(f"honeypot log write failed: {e}")


def peer_ip(extra_info_getter) -> str:
    """
    Best-effort peer IP extraction from a connection/writer/transport object.

    :param extra_info_getter: Object exposing get_extra_info('peername')
        (asyncssh connection, asyncio StreamWriter, ...).
    :return: The client IP as string, or 'unknown' when unavailable.
    """
    try:
        peername = extra_info_getter.get_extra_info('peername')
        return str(peername[0]) if peername and peername[0] else "unknown"
    except Exception:
        return "unknown"
