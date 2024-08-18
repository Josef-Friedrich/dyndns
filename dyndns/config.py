"""Load and validate the configuration."""

from __future__ import annotations

import ipaddress
import os
import re
from io import TextIOWrapper
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

import yaml
from pydantic import BaseModel, ConfigDict
from typing_extensions import NotRequired

from dyndns.exceptions import ConfigurationError, DnsNameError, IpAddressesError
from dyndns.ipaddresses import validate as validate_ip
from dyndns.names import validate_dns_name
from dyndns.zones import ZoneConfigNg, ZonesCollection

if TYPE_CHECKING:
    from dyndns.zones import ZoneConfig


class ConfigNg(BaseModel):
    model_config = ConfigDict(extra="forbid")

    secret: str
    """A password-like secret string. The secret string must be at least
    8 characters long and only alphanumeric characters are permitted."""

    nameserver: ipaddress.IPv4Address | ipaddress.IPv6Address
    """The IP address of your nameserver. Version 4 or
    version 6 are allowed. Use ``127.0.0.1`` to communicate with your
    nameserver on the same machine."""

    port: int
    """The port to which the DNS server listens. If the DNS server listens to
    port 53 by default, the value does not need to be specified."""

    zones: list["ZoneConfigNg"]
    """At least one zone specified as a list."""


class Config(TypedDict):
    secret: str
    """A password-like secret string. The secret string must be at least
    8 characters long and only alphanumeric characters are permitted."""

    nameserver: str
    """The IP address of your nameserver. Version 4 or
    version 6 are allowed. Use ``127.0.0.1`` to communicate with your
    nameserver on the same machine."""

    port: int

    dyndns_domain: NotRequired[str]
    """The domain through which the ``dyndns`` HTTP API is
    provided. This key is only used in the usage page and can be omitted."""

    zones: list["ZoneConfig"]
    """At least one zone specified as a list."""


def load_config(config_file: str | Path | None = None) -> Config:
    """
    Load the configuration from the specified file or from the default locations.

    :param config_file: The path to the configuration file. If not provided, the function will search for the configuration file in the default locations.

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

    for _config_file in config_files:
        if os.path.exists(_config_file):
            config_file = _config_file
            break

    if not config_file:
        raise ConfigurationError("The configuration file could not be found.")

    stream: TextIOWrapper = open(config_file, "r")
    config: Config = yaml.safe_load(stream)
    stream.close()
    return config


def validate_secret(secret: Any) -> str:
    secret = str(secret)
    if re.match("^[a-zA-Z0-9]+$", secret) and len(secret) >= 8:
        return secret
    raise ConfigurationError(
        "The secret must be at least 8 characters "
        "long and may not contain any "
        "non-alpha-numeric characters."
    )


def validate_config(config: Any = None) -> Config:
    if not config:
        try:
            config = load_config()
        except IOError:
            raise ConfigurationError("The configuration file could not be found.")
        except yaml.error.YAMLError:
            raise ConfigurationError(
                "The configuration file is in a invalid YAML format."
            )

    if not config:
        raise ConfigurationError("The configuration file could not be " "found.")

    if "secret" not in config:
        raise ConfigurationError(
            'Your configuration must have a "secret" '
            'key, for example: "secret: VDEdxeTKH"'
        )

    config["secret"] = validate_secret(config["secret"])

    if "nameserver" not in config:
        raise ConfigurationError(
            'Your configuration must have a "nameserver" '
            'key, for example: "nameserver: 127.0.0.1"'
        )

    try:
        validate_ip(config["nameserver"])
    except IpAddressesError:
        msg: str = (
            'The "nameserver" entry in your configuration is not a valid '
            f'IP address: "{config["nameserver"]}".'
        )
        raise ConfigurationError(msg)

    if "port" in config:
        if not isinstance(config["port"], int):
            raise ConfigurationError("Port has to be an int.")
    else:
        config["port"] = 53

    if "dyndns_domain" in config:
        try:
            validate_dns_name(config["dyndns_domain"])
        except DnsNameError as error:
            raise ConfigurationError(str(error))

    if "zones" not in config:
        raise ConfigurationError('Your configuration must have a "zones" key.')

    if not isinstance(config["zones"], (list,)):
        raise ConfigurationError('Your "zones" key must contain a list of ' "zones.")

    if not config["zones"]:
        raise ConfigurationError(
            "You must have at least one zone configured, "
            'for example: "- name: example.com" and '
            '"tsig_key: tPyvZA=="'
        )

    for zone in config["zones"]:
        if "name" not in zone:
            raise ConfigurationError(
                "Your zone dictionary must contain a key " '"name"'
            )

        if "tsig_key" not in zone:
            raise ConfigurationError(
                "Your zone dictionary must contain a key " '"tsig_key"'
            )

    try:
        config["zones"] = ZonesCollection(config["zones"])
    except DnsNameError as error:
        raise ConfigurationError(str(error))

    return config


def get_config(config_file: str | None = None) -> Config:
    return validate_config(load_config(config_file))
