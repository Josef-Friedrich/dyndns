"""Deal with different kind of names (FQDNs (Fully Qualified Domain Names),
record and zone names)

``record_name`` + ``zone_name`` = ``fqdn``

"""

from __future__ import annotations

import binascii
import re
import typing

import dns.name
import dns.tsig
import dns.tsigkeyring

from dyndns.exceptions import NamesError
from dyndns.types import ZoneConfig


def validate_hostname(hostname: str) -> str:
    """
    Validates the given hostname.

    :param hostname: The hostname to be validated.

    :return: The validated hostname as a string.
    """
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    if len(hostname) > 253:
        raise NamesError(
            'The hostname "{}..." is longer than 253 characters.'.format(hostname[:10])
        )

    labels: list[str] = hostname.split(".")

    tld: str = labels[-1]
    if re.match(r"[0-9]+$", tld):
        raise NamesError(
            'The TLD "{}" of the hostname "{}" must be not all-numeric.'.format(
                tld, hostname
            )
        )

    allowed: re.Pattern[str] = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    for label in labels:
        if not allowed.match(label):
            raise NamesError(
                'The label "{}" of the hostname "{}" is invalid.'.format(
                    label, hostname
                )
            )

    return str(dns.name.from_text(hostname))


def validate_tsig_key(tsig_key: str) -> str:
    """
    Validates a TSIG key.

    :param tsig_key: The TSIG key to validate.

    :return: The validated TSIG key.

    :raises NamesError: If the TSIG key is invalid.
    """
    if not tsig_key:
        raise NamesError('Invalid tsig key: "{}".'.format(tsig_key))
    try:
        dns.tsigkeyring.from_text({"tmp.org.": tsig_key})
        return tsig_key
    except binascii.Error:
        raise NamesError('Invalid tsig key: "{}".'.format(tsig_key))


class Zone:
    zone_name: str
    """The zone name (e. g. ``example.com.``)."""

    tsig_key: str
    """The TSIG (Transaction SIGnature) key (e. g. ``tPyvZA==``)."""

    def __init__(self, zone_name: str, tsig_key: str) -> None:
        """
        Initialize a Zone object.

        :param zone_name: The zone name (e. g. ``example.com.``).
        :param tsig_key: The TSIG (Transaction SIGnature) key (e. g. ``tPyvZA==``).
        """

        self.zone_name = validate_hostname(zone_name)
        self.tsig_key = validate_tsig_key(tsig_key)

    def split_fqdn(self, fqdn: str) -> tuple[str, str]:
        """Split hostname into record_name and zone_name
        for example: www.example.com -> www. example.com.

        :param fqdn: The fully qualified domain name.

        :return: A tuple containing the record_name and zone_name.

        :raises NamesError: If the FQDN is not splitable by the zone.

        """
        fqdn = validate_hostname(fqdn)
        record_name: str = fqdn.replace(self.zone_name, "")
        if record_name and len(record_name) < len(fqdn):
            return (record_name, self.zone_name)
        raise NamesError('FQDN "{}" is not splitable by zone "{}".')

    def build_fqdn(self, record_name: str) -> str:
        """
        Build a fully qualified domain name.

        :param record_name: The record name.

        :return: The fully qualified domain name.
        """
        record_name = validate_hostname(record_name)
        return record_name + self.zone_name


class ZonesCollection:
    zones: dict[str, Zone]

    def __init__(self, zones_config: list[ZoneConfig]) -> None:
        self.zones = {}
        for zone_config in zones_config:
            zone = Zone(zone_name=zone_config["name"], tsig_key=zone_config["tsig_key"])
            self.zones[zone.zone_name] = zone

    def get_zone_by_name(self, zone_name: str) -> Zone:
        zone_name = validate_hostname(zone_name)
        if zone_name in self.zones:
            return self.zones[validate_hostname(zone_name)]
        raise NamesError('Unkown zone "{}".'.format(zone_name))

    def split_fqdn(self, fqdn: str) -> tuple[str, str] | typing.Literal[False]:
        """Split hostname into record_name and zone_name
        for example: www.example.com -> www. example.com.
        """
        fqdn = validate_hostname(fqdn)
        # To handle subzones (example.com and dyndns.example.com)
        results: dict[int, tuple[str, str]] = {}
        for _, zone in self.zones.items():
            record_name: str = fqdn.replace(zone.zone_name, "")
            if record_name and len(record_name) < len(fqdn):
                results[len(record_name)] = (record_name, zone.zone_name)
        for key in sorted(results):
            return results[key]
        return False


class DomainName:
    """
    Stores a FQDN (Fully Qualified Domain Names),
    a zone name and a record along with the TSIG (Transaction SIGnature) key.

    ``record_name`` + ``zone_name`` = ``fqdn``
    """

    fqdn: str
    """The Fully Qualified Domain Name (e. g. ``www.example.com.``)."""

    zone_name: str
    """The zone name (e. g. ``example.com.``)."""

    record_name: str
    """The name of the resource record (e. g. ``www.``)."""

    tsig_key: str
    """The TSIG (Transaction SIGnature) key (e. g. ``tPyvZA==``)"""

    def __init__(
        self,
        zones: ZonesCollection,
        fqdn: str | None = None,
        zone_name: str | None = None,
        record_name: str | None = None,
    ) -> None:
        """
        Initialize the ``DomainName`` object.

        :param zones: The ZonesCollection object.
        :param fqdn: The Fully Qualified Domain Name (e. g. ``www.example.com.``).
        :param zone_name: The zone name (e. g. ``example.com.``).
        :param record_name: The name of the resource record (e. g. ``www.``).

        :raises NamesError: If both fqdn and zone_name/record_name are specified.
        :raises NamesError: If record_name is not provided.
        :raises NamesError: If zone_name is not provided.
        """
        if fqdn and zone_name and record_name:
            raise NamesError('Specify "fqdn" or "zone_name" and "record_name".')

        self._zones: ZonesCollection = zones

        if fqdn:
            self.fqdn = validate_hostname(fqdn)
            split = self._zones.split_fqdn(fqdn)
            if split:
                self.record_name = split[0]
                self.zone_name = split[1]

        if not fqdn and zone_name and record_name:
            self.record_name = validate_hostname(record_name)
            self.zone_name = validate_hostname(zone_name)
            zone = self._zones.get_zone_by_name(self.zone_name)
            self.fqdn = zone.build_fqdn(self.record_name)

        if not self.record_name:
            raise NamesError('Value "record_name" is required.')

        if not self.zone_name:
            raise NamesError('Value "zone_name" is required.')

        self._zone = self._zones.get_zone_by_name(self.zone_name)
        self.tsig_key = self._zone.tsig_key
