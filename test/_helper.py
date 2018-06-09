import os
import socket
from jfddns.names import Zones


def check_internet_connectifity(host="8.8.8.8", port=53, timeout=3):
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


files_dir = os.path.join(os.path.dirname(__file__), 'files')
config_file = os.path.join(files_dir, 'config.yml')


zones = Zones([
    {'name': 'example.com.', 'tsig_key': 'tPyvZA=='},
    {'name': 'example.org', 'tsig_key': 'tPyvZA=='},
])
