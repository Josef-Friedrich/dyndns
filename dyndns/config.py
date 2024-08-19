"""Load and validate the configuration."""

from __future__ import annotations

import binascii
import ipaddress
import os
import re
from io import TextIOWrapper
from pathlib import Path
from typing import Annotated, Any, Literal

import dns
import dns.name
import dns.tsigkeyring
import yaml
from annotated_types import Len
from dns.name import from_text as create_name_from_text
from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import AfterValidator

from dyndns.exceptions import ConfigurationError, DnsNameError, IpAddressesError

RecordType = Literal["A", "AAAA", "TXT"]

IpVersion = Literal[4, 6]


def validate_ip_address_by_version(
    address: Any, ip_version: IpVersion | None = None
) -> tuple[str, IpVersion]:
    try:
        address = ipaddress.ip_address(address)
        if ip_version and ip_version != address.version:
            raise IpAddressesError(f'IP version "{ip_version}" does not match.')
        return str(address), address.version
    except ValueError:
        raise IpAddressesError(f"Invalid IP address '{address}'.")


def validate_ip_address(address: str) -> str:
    ipaddress.ip_address(address)
    return address


IpAddress = Annotated[str, AfterValidator(validate_ip_address)]


def validate_secret(secret: str) -> str:
    assert (
        len(secret) >= 8
    ), f"The secret must be at least 8 characters long. Currently the string is {len(secret)} characters long."

    non_alphanumeric: str = re.sub(r"[a-zA-Z0-9]", "", secret)

    assert (
        len(non_alphanumeric) == 0
    ), f"The secret must not contain any non-alphanumeric characters. These characters are permitted: [a-zA-Z0-9]. The following characters are not alphanumeric '{non_alphanumeric}'."
    return secret


Secret = Annotated[str, AfterValidator(validate_secret)]


def validate_port(port: int) -> int:
    assert (
        port > -1 and port < 65536
    ), f"The port number has to be between '0' and '65535', not '{port}'."
    return port


Port = Annotated[int, AfterValidator(validate_port)]


def validate_name(name: str) -> str:
    """
    Validate the given DNS name. A dot is appended to the end of the DNS name
    if it is not already present.

    :param name: The DNS name to be validated.

    :return: The validated DNS name as a string.
    """
    dns_name = create_name_from_text(name)

    if name[-1] == ".":
        # strip exactly one dot from the right, if present
        name = name[:-1]

    labels: list[str] = name.split(".")

    # https://stackoverflow.com/a/53875771
    top_level_domain: str = labels[-1]
    if re.match(r"[0-9]+$", top_level_domain):
        raise DnsNameError(
            f"The TLD '{top_level_domain}' of the DNS name '{name}' must be not purely numeric."
        )

    allowed: re.Pattern[str] = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    for label in labels:
        if not allowed.match(label):
            raise DnsNameError(
                f"The label '{label}' of the DNS name '{name}' is invalid."
            )
    return str(dns_name)


Name = Annotated[str, AfterValidator(validate_name)]


def validate_tsig_key(tsig_key: str) -> str:
    """
    Validates a TSIG key.

    :param tsig_key: The TSIG key to validate.

    :return: The validated TSIG key.

    :raises NamesError: If the TSIG key is invalid.
    """
    if not tsig_key:
        raise DnsNameError(f'Invalid tsig key: "{tsig_key}".')
    try:
        dns.tsigkeyring.from_text({"tmp.org.": tsig_key})
        return tsig_key
    except binascii.Error:
        raise DnsNameError(f'Invalid tsig key: "{tsig_key}".')


TsigKey = Annotated[str, AfterValidator(validate_tsig_key)]


class ZoneConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Name
    """The domain name of the zone, for example
      ``dyndns.example.com``."""

    tsig_key: TsigKey
    """The tsig-key. Use the ``hmac-sha512`` algorithm to
      generate the key:
      ``tsig-keygen -a hmac-sha512 dyndns.example.com``"""


ZonesList = Annotated[list["ZoneConfig"], Len(min_length=1)]


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")

    secret: Secret
    """A password-like secret string. The secret string must be at least
    8 characters long and only alphanumeric characters are permitted."""

    nameserver: ipaddress.IPv4Address | ipaddress.IPv6Address
    """The IP address of your nameserver. Version 4 or
    version 6 are allowed. Use ``127.0.0.1`` to communicate with your
    nameserver on the same machine."""

    port: Port = 53
    """The port to which the DNS server listens. If the DNS server listens to
    port 53 by default, the value does not need to be specified."""

    log_level: Annotated[int, Field(ge=0, le=50)] = 20
    """
    Values from 0 (everything is logged) to 50 (only critical message are logged) are allowed.
    The default value is ``20``.

    :see: :class:`dyndns.log.LogLevel`
    """

    zones: ZonesList
    """At least one zone specified as a list."""


def load_config(config_file: str | Path | None = None) -> Config:
    """
    Load the configuration from the specified file or from the default locations.

    :param config_file: The path to the configuration file. If not provided, the
        function will search for the configuration file in the default locations.

    :return: The loaded configuration as a dictionary.

    :raises ConfigurationError: If the configuration file could not be found.
    """
    config_files: list[str] = []
    if config_file:
        config_files.append(str(config_file))
    if "dyndns_CONFIG_FILE" in os.environ:
        config_files.append(os.environ["dyndns_CONFIG_FILE"])
    config_files.append(os.path.join(os.getcwd(), ".dyndns.yml"))
    config_files.append("/etc/dyndns.yml")

    for path in config_files:
        if os.path.exists(path):
            config_file = path
            break

    if not config_file:
        raise ConfigurationError("The configuration file could not be found.")

    stream: TextIOWrapper = open(config_file, "r")
    config_raw = yaml.safe_load(stream)
    stream.close()
    return Config(**config_raw)
