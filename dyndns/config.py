"""Load and validate the configuration."""

from __future__ import annotations

import os
import re
from io import TextIOWrapper
from typing import Any

import yaml

from dyndns.exceptions import ConfigurationError, DnsNameError, IpAddressesError
from dyndns.ipaddresses import validate as validate_ip
from dyndns.names import validate_dns_name
from dyndns.types import Config
from dyndns.zones import ZonesCollection


def load_config(config_file: str | None = None) -> Config:
    """
    Load the configuration from the specified file or from the default locations.

    :param config_file: The path to the configuration file. If not provided, the function will search for the configuration file in the default locations.

    :return: The loaded configuration as a dictionary.

    :raises ConfigurationError: If the configuration file could not be found.
    """
    config_files: list[str] = []
    if config_file:
        config_files.append(config_file)
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
