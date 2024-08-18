from typing import Iterator

from dyndns.config import ZoneConfig, validate_name, validate_tsig_key
from dyndns.exceptions import DnsNameError


class Zone:
    """
    Stores the zone name together with the corresponding TSIG (Transaction SIGnature) key.

    :param zone_name: The zone name (e. g. ``example.com.``).
    :param tsig_key: The TSIG (Transaction SIGnature) key (e. g. ``tPyvZA==``).
    """

    name: str
    """The zone name (e. g. ``example.com.``)."""

    tsig_key: str
    """The TSIG (Transaction SIGnature) key (e. g. ``tPyvZA==``)."""

    def __init__(self, name: str, tsig_key: str) -> None:
        """
        Initialize a Zone object.

        :param name: The zone name (e. g. ``example.com.``).
        :param tsig_key: The TSIG (Transaction SIGnature) key (e. g. ``tPyvZA==``).
        """
        self.name = validate_name(name)
        self.tsig_key = validate_tsig_key(tsig_key)

    def get_record_name(self, name: str) -> str:
        """
        Remove the zone from the given DNS name.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
          domain name (e. g. ``dyndns.example.com``).

        :return: The record name (e. g. ``dyndns.``).
        """
        return validate_name(name).replace(self.name, "")

    def get_fqdn(self, name: str) -> str:
        """
        Build a fully qualified domain name.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
          domain name (e. g. ``dyndns.example.com``).

        :return: The fully qualified domain name.
        """
        return self.get_record_name(name) + self.name

    def split_fqdn(self, name: str) -> tuple[str, str]:
        """Split hostname into record_name and zone_name
        for example: www.example.com -> www. example.com.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
          domain name (e. g. ``dyndns.example.com``).

        :return: A tuple containing the record name and zone name.
        """
        return (self.get_record_name(name), self.name)


class ZonesCollection:
    zones: dict[str, Zone]

    def __init__(self, zones_config: list[ZoneConfig]) -> None:
        self.zones = {}
        for zone_config in zones_config:
            zone = Zone(name=zone_config.name, tsig_key=zone_config.tsig_key)
            self.zones[zone.name] = zone
        self._iter_index = 0
        self._zone_keys = list(self.zones.keys())

    def __iter__(self) -> Iterator[Zone]:
        self._iter_index = 0
        self._zone_keys = list(self.zones.keys())
        return self

    def __next__(self) -> Zone:
        if self._iter_index < len(self._zone_keys):
            zone_name = self._zone_keys[self._iter_index]
            self._iter_index += 1
            return self.zones[zone_name]
        else:
            raise StopIteration

    def get_zone(self, name: str) -> Zone:
        """
        Get a zone by a DNS name.

        :param name: The DNS name. It can be a fully qualified domain name
          containing the zone name or the zone name itself.

        :return: The requested zone.

        :raises DnsNameError: if the zone could not be found.
        """
        segments = self.split_fqdn(name)
        if segments is None:
            raise DnsNameError(f'Unknown zone "{name}".')
        return self.zones[segments[1]]

    def split_fqdn(self, fqdn: str) -> tuple[str, str] | None:
        """Split a fully qualified domain name into a record name and a zone name,
        for example: ``www.example.com`` -> ``www.`` ``example.com.``

        :param fqdn: The fully qualified domain name.

        :return: A tuple containing two entries: The first is the record name and the second is the zone name.
        """
        fqdn = validate_name(fqdn)
        # To handle subzones (example.com and dyndns.example.com)
        results: dict[int, tuple[str, str]] = {}
        for _, zone in self.zones.items():
            if zone.name in fqdn:
                record_name: str = fqdn.replace(zone.name, "")
                results[len(record_name)] = (record_name, zone.name)
        for key in sorted(results):
            return results[key]
        return None
