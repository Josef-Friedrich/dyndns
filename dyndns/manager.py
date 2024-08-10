"""Main class that assembles all classes together with the loaded configuration."""

from typing import Any, Generator

from dyndns.config import load_config
from dyndns.dns_ng import DnsZone
from dyndns.types import Config
from dyndns.zones import ZonesCollection


class Manager:
    _config: Config

    _zones: ZonesCollection

    _dns_zones: dict[str, DnsZone]

    def __init__(self, config_file: str | None = None) -> None:
        self._config = load_config(config_file)
        self._zones = ZonesCollection(self._config["zones"])

        self._dns_zones = {}

        for zone in self._zones:
            self._dns_zones[zone.zone_name] = DnsZone(self._config["nameserver"], zone)

    def _get_dns_zone(self, zone_name: str) -> DnsZone:
        return self._dns_zones[zone_name]

    @property
    def dns_zones(self) -> Generator[DnsZone, Any, Any]:
        for dns_zone in self._dns_zones.values():
            yield dns_zone

    def check(self) -> None:
        for dns_zone in self.dns_zones:
            dns_zone.check()
