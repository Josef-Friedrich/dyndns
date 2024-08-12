"""Query the DSN server using the package “dnspython”."""

from __future__ import annotations

from typing import Any, Literal

import dns.exception
import dns.name
import dns.query
import dns.resolver
import dns.tsig
import dns.tsigkeyring
import dns.update

from dyndns.exceptions import DNSServerError, DyndnsError
from dyndns.ipaddresses import IpAddressContainer
from dyndns.log import logger
from dyndns.names import FullyQualifiedDomainName
from dyndns.types import IpVersion, LogLevel, RecordType, UpdateRecord


class DnsUpdate:
    """
    Update the DNS server.

    :param nameserver: The ip address of the nameserver, for example ``127.0.0.1``.
    """

    nameserver: str
    """The ip address of the nameserver, for example ``127.0.0.1``."""

    fqdn: FullyQualifiedDomainName

    ipaddresses: IpAddressContainer | None

    ttl: int
    """time to live"""

    def __init__(
        self,
        nameserver: str,
        names: FullyQualifiedDomainName,
        ipaddresses: IpAddressContainer | None = None,
        ttl: str | int | None = None,
    ) -> None:
        self.nameserver = nameserver
        self.fqdn = names
        self.ipaddresses = ipaddresses
        if not ttl:
            self.ttl = 300
        else:
            self.ttl = int(ttl)

        self._tsigkeyring: dns.name.Dict[dns.name.Name, dns.tsig.Key] = (
            self._build_tsigkeyring(
                self.fqdn.zone_name,
                self.fqdn.tsig_key,
            )
        )
        self._dns_update: dns.update.Update = dns.update.Update(
            self.fqdn.zone_name,
            keyring=self._tsigkeyring,
            keyalgorithm=dns.tsig.HMAC_SHA512,
        )

    @staticmethod
    def _build_tsigkeyring(
        zone_name: str, tsig_key: str
    ) -> dns.name.Dict[dns.name.Name, dns.tsig.Key]:
        """
        :param zone: A zone name object
        :param tsig_key: A TSIG key
        """
        keyring: dict[str, str] = {}
        keyring[zone_name] = tsig_key
        return dns.tsigkeyring.from_text(keyring)

    @staticmethod
    def _convert_record_type(ip_version: Any = 4) -> RecordType:
        if ip_version == 4:
            return "a"
        elif ip_version == 6:
            return "aaaa"
        else:
            raise ValueError("“ip_version” must be 4 or 6")

    def _resolve(self, ip_version: IpVersion = 4) -> str:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [self.nameserver]
        try:
            ip: dns.resolver.Answer = resolver.resolve(
                self.fqdn.fqdn,
                self._convert_record_type(ip_version),
            )
            return str(ip[0])  # type: ignore
        except dns.exception.DNSException:
            return ""

    def _query_tcp(self, dns_update: dns.update.Update) -> None:
        """Catch some errors and convert this errors to dyndns specific
        errors."""
        try:
            dns.query.tcp(dns_update, where=self.nameserver, timeout=5)
        except dns.tsig.PeerBadKey:
            raise DNSServerError(
                f'The peer "{self.nameserver}" didn\'t know the tsig key '
                f'we used for the zone "{self.fqdn.zone_name}".'
            )
        except dns.exception.Timeout:
            raise DNSServerError(
                f'The DNS operation to the nameserver "{self.nameserver}" timed out.'
            )

    def _set_record(self, new_ip: str, ip_version: IpVersion = 4) -> UpdateRecord:
        old_ip: str = self._resolve(ip_version)
        rdtype = self._convert_record_type(ip_version)

        status: LogLevel

        if new_ip == old_ip:
            status = LogLevel.UNCHANGED
            logger.log_update(False, self.fqdn.fqdn, rdtype, new_ip)
        else:
            self._dns_update.delete(self.fqdn.fqdn, rdtype)
            # If the client (a notebook) moves in a network without ipv6
            # support, we have to delete the 'aaaa' record.
            if rdtype == "a":
                self._dns_update.delete(self.fqdn.fqdn, "aaaa")

            self._dns_update.add(self.fqdn.fqdn, self.ttl, rdtype, new_ip)
            self._query_tcp(self._dns_update)

            checked_ip = self._resolve(ip_version)

            if new_ip == checked_ip:
                status = LogLevel.UPDATED
                logger.log_update(True, self.fqdn.fqdn, rdtype, new_ip)
            else:
                status = LogLevel.DNS_SERVER_ERROR

        return {
            "ip_version": ip_version,
            "new_ip": new_ip,
            "old_ip": old_ip,
            "status": status,
        }

    def delete(self) -> Literal[True]:
        self._dns_update.delete(self.fqdn.fqdn, "a")
        self._dns_update.delete(self.fqdn.fqdn, "aaaa")
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
