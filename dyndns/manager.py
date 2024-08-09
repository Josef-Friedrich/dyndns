"""Main class that assembles all classes together with the loaded configuration."""

from dyndns.config import load_config
from dyndns.dns_ng import DnsZone
from dyndns.names import ZonesCollection
from dyndns.types import Config


class Manager:
    _config: Config

    _zone_managers: dict[str, DnsZone]

    _zones: ZonesCollection

    def __init__(self, config_file: str | None = None) -> None:
        self._config = load_config(config_file)
        self._zone_managers = {}
        self._zones = ZonesCollection(self._config["zones"])

    def get_dns_zone(self, zone_name: str) -> DnsZone:
        if zone_name not in self._zone_managers:
            self._zone_managers[zone_name] = DnsZone(
                self._config["nameserver"], self._zones.get_zone_by_name(zone_name)
            )
        return self._zone_managers[zone_name]
