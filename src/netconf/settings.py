import os
import typing as t
from dataclasses import dataclass


@dataclass
class Settings:
    """
    pytest-netconf settings.
    """

    base_version: t.Literal["1.0", "1.1"] = os.getenv("NETCONF_VERSION", "1.1")
    host: str = os.getenv("NETCONF_HOST", "localhost")
    port: int = int(os.getenv("NETCONF_PORT", "8830"))
    username: t.Optional[str] = os.getenv("NETCONF_USERNAME")
    password: t.Optional[str] = os.getenv("NETCONF_PASSWORD")
    authorized_key: t.Optional[str] = os.getenv("NETCONF_AUTHORIZED_KEY")
    allocate_pty: bool = bool(
        (os.getenv("NETCONF_AUTHORIZED_KEY", "true")).lower() == "true"
    )
