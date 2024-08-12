"""Main class that assembles all classes together with the loaded configuration."""

from typing import Any, Generator

import flask

from dyndns.config import load_config
from dyndns.dns import DnsUpdate
from dyndns.dns_ng import DnsZone
from dyndns.exceptions import (
    ParameterError,
)
from dyndns.ipaddresses import IpAddressContainer
from dyndns.log import logger
from dyndns.names import FullyQualifiedDomainName
from dyndns.types import Config, LogLevel, UpdateRecord
from dyndns.zones import ZonesCollection


class ConfiguredEnvironment:
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

    def check(self) -> str:
        outputs: list[str] = []
        for dns_zone in self.dns_zones:
            outputs.append(dns_zone.check())
        return "\n".join(outputs)

    def _authenticate(self, secret: Any) -> None:
        if str(secret) != str(self._config["secret"]):
            raise ParameterError("You specified a wrong secret key.")

    def update_dns_record(
        self,
        secret: str | None = None,
        fqdn: str | None = None,
        zone_name: str | None = None,
        record_name: str | None = None,
        ip_1: str | None = None,
        ip_2: str | None = None,
        ipv4: str | None = None,
        ipv6: str | None = None,
        ttl: int | None = None,
    ) -> str:
        """
        Update a DNS record.

        :param secret: A password like secret string. The secret string has to
        be at least 8 characters long and only alphnumeric characters are
        allowed.
        :param fqdn: The Fully-Qualified Domain Name
        (e. g. ``www.example.com``). If you specify the argument ``fqdn``, you
        don’t have to specify the arguments ``zone_name`` and ``record_name``.
        :param zone_name: The zone name (e. g. ``example.com``). You have to
        specify the argument ``record_name``.
        :param record_name: The record name (e. g. ``www``). You have to
        specify the argument ``zone_name``.
        :param ip_1: An IP address, can be version 4 or version 6.
        :param ip_2: A second IP address, can be version 4 or version 6. Must
        be a different version than ``ip_1``.
        :param ipv4: An IP address version 4.
        :param ipv6: An IP address version 6.
        :param ttl: Time to live.
        :param dict config: The configuration in the Python dictionary format
        (as returned by the function ``validate_config()``).
        """

        self._authenticate(secret)

        names = FullyQualifiedDomainName(
            self._zones,
            fqdn=fqdn,
            zone_name=zone_name,
            record_name=record_name,
        )
        ip_addresses = IpAddressContainer(
            ip_1=ip_1,
            ip_2=ip_2,
            ipv4=ipv4,
            ipv6=ipv6,
            request=flask.request,
        )

        update = DnsUpdate(
            nameserver=self._config["nameserver"],
            names=names,
            ipaddresses=ip_addresses,
            ttl=ttl,
        )
        results: list[UpdateRecord] = update.update()

        messages: list[str] = []
        for result in results:
            message = "fqdn: {} old_ip: {} new_ip: {}".format(
                names.fqdn, result["old_ip"], result["new_ip"]
            )
            messages.append(logger.log(result["status"], message))

        return "".join(messages)

    def delete_dns_record(
        self, secret: str | None = None, fqdn: str | None = None
    ) -> str:
        self._authenticate(secret)

        names = FullyQualifiedDomainName(self._zones, fqdn=fqdn)

        delete = DnsUpdate(
            nameserver=self._config["nameserver"],
            names=names,
        )

        if delete.delete():
            return logger.log(LogLevel.UPDATED, f'Deleted "{names.fqdn}".')
        return logger.log(
            LogLevel.UNCHANGED, f'Deletion not successful "{names.fqdn}".'
        )


_environment: ConfiguredEnvironment | None = None


def get_environment(config_file: str | None = None) -> ConfiguredEnvironment:
    global _environment
    if not _environment:
        _environment = ConfiguredEnvironment(config_file)
    return _environment
