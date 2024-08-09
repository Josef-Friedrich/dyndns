#! /usr/bin/env python

import random
import string
from typing import Any

import dns.message
import dns.name
import dns.query
import dns.resolver
import dns.tsig
import dns.tsigkeyring
import dns.update

from dyndns.config import get_config
from dyndns.names import Zone, ZonesCollection
from dyndns.types import Config

config: Config = get_config()


class DnsZoneManager:
    _nameserver: str
    """The ip address of the nameserver, for example ``127.0.0.1``."""

    _zone: Zone

    _keyring: dict[dns.name.Name, dns.tsig.Key]

    __resolver: dns.resolver.Resolver

    def __init__(self, nameserver: str, zone: Zone) -> None:
        self._nameserver = nameserver
        self._zone = zone
        self._keyring = dns.tsigkeyring.from_text({zone.zone_name: zone.tsig_key})

    @property
    def _resolver(self) -> dns.resolver.Resolver:
        if not hasattr(self, "__resolver"):
            self.__resolver = dns.resolver.Resolver()
            self.__resolver.nameservers = [self._nameserver]
        return self.__resolver

    def _create_update_message(self) -> dns.update.UpdateMessage:
        return dns.update.UpdateMessage(
            self._zone.zone_name,
            keyring=self._keyring,
            keyalgorithm=dns.tsig.HMAC_SHA512,
        )

    def _query(self, message: dns.message.Message) -> dns.message.Message:
        return dns.query.tcp(message, self._nameserver)

    def delete_record(self, record_name: str, rdtype: str = "A") -> None:
        message: dns.update.UpdateMessage = self._create_update_message()
        message.delete(record_name, rdtype)
        self._query(message)

    def add_record(self, record_name: str, ttl: int, rdtype: str, content: str) -> None:
        message = self._create_update_message()
        message.add(record_name, ttl, rdtype, content)
        self._query(message)

    def read_record(self, record_name: str, rdtype: str) -> dns.resolver.Answer:
        return self._resolver.resolve(record_name + "." + self._zone.zone_name, rdtype)

    def check(self) -> None:
        check_record_name = "dyndns-check-tmp_a841278b-f089-4164-b8e6-f90514e573ec"
        random_content = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )
        self.delete_record(check_record_name, "TXT")
        self.add_record(check_record_name, 300, "TXT", random_content)
        result: Any = self.read_record(check_record_name, "TXT")
        if result.strings[0].decode() != random_content:
            raise Exception("check failed")
        self.delete_record(check_record_name, "TXT")


zone_managers: dict[str, DnsZoneManager] = {}

zones = ZonesCollection(config["zones"])


def get_dns_zone_manager(zone_name: str) -> DnsZoneManager:
    if zone_name not in zone_managers:
        zone_managers[zone_name] = DnsZoneManager(
            config["nameserver"], zones.get_zone_by_name(zone_name)
        )
    return zone_managers[zone_name]
