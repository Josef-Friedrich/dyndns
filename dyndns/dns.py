"""Query the DSN server using the package “dnspython”."""

from __future__ import annotations

import typing

import dns.exception
import dns.name
import dns.query
import dns.resolver
import dns.tsig
import dns.tsigkeyring
import dns.update

from dyndns.exceptions import DNSServerError, DyndnsError
from dyndns.ipaddresses import IpAddressContainer
from dyndns.log import UpdatesDB
from dyndns.names import Names
from dyndns.types import IpVersion, RecordType, UpdateRecord


class DnsUpdate:
    """
    Update the DNS server
    """

    nameserver: str
    """for example ``127.0.0.1``"""

    names: Names

    ipaddresses: IpAddressContainer | None

    ttl: int

    def __init__(
        self,
        nameserver: str,
        names: Names,
        ipaddresses: IpAddressContainer | None = None,
        ttl: str | int | None = None,
    ) -> None:
        self.nameserver = nameserver  #: The nameserver
        self.names = names
        self.ipaddresses = ipaddresses
        if not ttl:
            self.ttl = 300
        else:
            self.ttl = int(ttl)

        self._tsigkeyring = self._build_tsigkeyring(
            self.names.zone_name,
            self.names.tsig_key,
        )
        self._dns_update: dns.update.Update = dns.update.Update(
            self.names.zone_name,
            keyring=self._tsigkeyring,
            keyalgorithm=dns.tsig.HMAC_SHA512,
        )
        self._updates_db = UpdatesDB()
        self.log_update = self._updates_db.log_update

    @staticmethod
    def _build_tsigkeyring(zone_name: str, tsig_key: str):
        """
        :param zone: A zone name object
        :param tsig_key: A TSIG key
        """
        keyring: dict[str, str] = {}
        keyring[zone_name] = tsig_key
        return dns.tsigkeyring.from_text(keyring)

    @staticmethod
    def _convert_record_type(ip_version: IpVersion = 4) -> RecordType:
        if ip_version == 4:
            return "a"
        elif ip_version == 6:
            return "aaaa"
        else:
            raise ValueError("“ip_version” must be 4 or 6")

    def _resolve(self, ip_version: IpVersion = 4):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [self.nameserver]
        try:
            ip: dns.resolver.Answer = resolver.query(
                self.names.fqdn,
                self._convert_record_type(ip_version),
            )
            return str(ip[0])
        except dns.exception.DNSException:
            return ""

    def _query_tcp(self, dns_update: dns.update.Update) -> None:
        """Catch some errors and convert this errors to dyndns specific
        errors."""
        try:
            dns.query.tcp(dns_update, where=self.nameserver, timeout=5)
        except dns.tsig.PeerBadKey:
            raise DNSServerError(
                'The peer "{}" didn\'t know the tsig key '
                'we used for the zone "{}".'.format(
                    self.nameserver,
                    self.names.zone_name,
                )
            )
        except dns.exception.Timeout:
            raise DNSServerError(
                "The DNS operation to the nameserver " '"{}" timed out.'.format(
                    self.nameserver
                )
            )

    def _set_record(self, new_ip: str, ip_version: IpVersion = 4) -> UpdateRecord:
        out = {}
        out["ip_version"] = ip_version
        out["new_ip"] = new_ip
        old_ip: str = self._resolve(ip_version)
        out["old_ip"] = old_ip
        rdtype = self._convert_record_type(ip_version)

        if new_ip == old_ip:
            out["status"] = "UNCHANGED"
            self.log_update(False, self.names.fqdn, rdtype, new_ip)
        else:
            self._dns_update.delete(self.names.fqdn, rdtype)
            # If the client (a notebook) moves in a network without ipv6
            # support, we have to delete the 'aaaa' record.
            if rdtype == "a":
                self._dns_update.delete(self.names.fqdn, "aaaa")

            self._dns_update.add(self.names.fqdn, self.ttl, rdtype, new_ip)
            self._query_tcp(self._dns_update)

            checked_ip = self._resolve(ip_version)

            if new_ip == checked_ip:
                out["status"] = "UPDATED"
                self.log_update(True, self.names.fqdn, rdtype, new_ip)
            else:
                out["status"] = "DNS_SERVER_ERROR"

        return typing.cast(UpdateRecord, out)

    def delete(self):
        self._dns_update.delete(self.names.fqdn, "a")
        self._dns_update.delete(self.names.fqdn, "aaaa")
        self._query_tcp(self._dns_update)
        return True

    def update(self) -> list[UpdateRecord]:
        results: list[UpdateRecord] = []
        if not self.ipaddresses:
            raise DyndnsError("No ip addresses set.")
        if self.ipaddresses.ipv4:
            results.append(self._set_record(new_ip=self.ipaddresses.ipv4, ip_version=4))
        if self.ipaddresses.ipv6:
            results.append(self._set_record(new_ip=self.ipaddresses.ipv6, ip_version=6))

        return results
