import os
import socket

from dyndns.log import UpdatesDB
from dyndns.names import ZonesCollection


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


files_dir = os.path.join(os.path.dirname(__file__), "files")
config_file = os.path.join(files_dir, "config.yml")


zones = ZonesCollection(
    [
        {"name": "example.com.", "tsig_key": "tPyvZA=="},
        {"name": "example.org", "tsig_key": "tPyvZA=="},
    ]
)


def get_updates_db() -> UpdatesDB:
    db = UpdatesDB()
    arguments_list = (
        (True, "c.example.com", "a", "1.2.3.4"),
        (False, "c.example.com", "a", "1.2.3.4"),
        (True, "c.example.com", "a", "2.2.3.4"),
        (True, "c.example.com", "a", "3.2.3.4"),
        (True, "c.example.com", "aaaa", "1::2"),
        (True, "c.example.com", "aaaa", "1::3"),
        (True, "b.example.com", "a", "1.2.3.4"),
        (False, "b.example.com", "a", "1.2.3.4"),
        (True, "a.example.com", "a", "1.2.3.4"),
        (True, "a.example.com", "a", "1.2.3.3"),
        (True, "a.example.com", "a", "1.2.3.2"),
        (False, "a.example.com", "a", "1.2.3.2"),
    )
    for arguments in arguments_list:
        db.log_update(*arguments)
    return db


def remove_updates_db() -> None:
    db_file = os.path.join(os.getcwd(), "dyndns.db")
    if os.path.exists(db_file):
        os.remove(db_file)
