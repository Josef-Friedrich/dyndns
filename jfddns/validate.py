import binascii
import dns.tsigkeyring
import ipaddress
import re


def secret(secret):
    secret = str(secret)
    if re.match('^[a-zA-Z0-9]+$', secret) and len(secret) >= 8:
        return secret
    else:
        return False


def ipv4(address):
    try:
        address = ipaddress.ip_address(address)
        if address.version == 4:
            return address
        else:
            return False
    except ValueError:
        return False


def ipv6(address):
    try:
        address = ipaddress.ip_address(address)
        if address.version == 6:
            return address
        else:
            return False
    except ValueError:
        return False


def tsig_key(tsig_key):
    if not tsig_key:
        return False
    try:
        dns.tsigkeyring.from_text({'tmp.org.': tsig_key})
        return tsig_key
    except binascii.Error:
        return False


def _hostname(hostname):
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    if len(hostname) > 253:
        return False

    labels = hostname.split(".")

    # the TLD must be not all-numeric
    if re.match(r"[0-9]+$", labels[-1]):
        return False

    allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(label) for label in labels)


def zone(zone_name):
    if _hostname(zone_name):
        return zone_name
    else:
        return False


def record(record_name):
    if _hostname(record_name):
        return record_name
    else:
        return False
