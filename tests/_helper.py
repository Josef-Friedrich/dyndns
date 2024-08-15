import os
import socket
from pathlib import Path

from dyndns.zones import ZonesCollection


def check_internet_connectifity(
    host: str = "8.8.8.8", port: int = 53, timeout: int = 3
) -> bool:
    """
    https://stackoverflow.com/a/33117579
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False


files_dir: str = os.path.join(os.path.dirname(__file__), "files")
config_file: str = os.path.join(files_dir, "config.yml")


IS_REAL_WORLD: bool = Path("/etc/dyndns.yml").exists()
"""True if a real DNS server is configured with a zone name ``dyndns.friedrich.rocks``."""

NOT_REAL_WORLD: bool = not IS_REAL_WORLD
"""True if a real DNS server is not configured."""

zones = ZonesCollection(
    [
        {"name": "example.com.", "tsig_key": "tPyvZA=="},
        {"name": "example.org", "tsig_key": "tPyvZA=="},
    ]
)
