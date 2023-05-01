from __future__ import annotations

from typing import Literal

from typing_extensions import NotRequired, TypedDict

LogLevel = Literal[
    "CONFIGURATION_ERROR", "DNS_SERVER_ERROR", "PARAMETER_ERROR", "UPDATED", "UNCHANGED"
]

RecordType = Literal["a", "aaaa"]

IpVersion = Literal[4, 6]


class ZoneConfig(TypedDict):
    name: str
    """The domain name of the zone, for example
      ``dyndns.example.com``."""

    tsig_key: str
    """The tsig-key. Use the ``hmac-sha512`` algorithm to
      generate the key:
      ``tsig-keygen -a hmac-sha512 dyndns.example.com``"""


class Config(TypedDict):
    secret: str
    """A password-like secret string. The secret string has to
  be at least 8 characters long and only alphnumeric characters are
  allowed."""

    nameserver: str
    """The IP address of your nameserver. Version 4 or
  version 6 are allowed. Use ``127.0.0.1`` to communicate with your
  nameserver on the same machine."""

    dyndns_domain: NotRequired[str]
    """The domain through which the ``dyndns`` HTTP API is
  provided. This key is only used in the usage page and can be omitted."""

    zones: list[ZoneConfig]
    """At least one zone specified as a list."""
