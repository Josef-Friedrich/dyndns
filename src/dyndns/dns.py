"""Query the DSN server using the package “dnspython”."""

import random
import string
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import dns.exception
import dns.message
import dns.name
import dns.query
import dns.rdatatype
import dns.resolver
import dns.rrset
import dns.tsig
import dns.tsigkeyring
import dns.update

from dyndns.config import RecordType
from dyndns.exceptions import CheckError, DNSServerError
from dyndns.log import LogLevel, logger

if TYPE_CHECKING:
    from dyndns.zones import Zone


@dataclass
class DnsChangeMessage:
    fqdn: str
    old: str | None
    new: str | None
    record_type: RecordType

    @property
    def changed(self) -> bool:
        return self.old != self.new


class DnsZone:
    _nameserver: str
    """The ip address of the nameserver, for example ``127.0.0.1``."""

    _port: int

    _zone: "Zone"

    _keyring: dict[dns.name.Name, dns.tsig.Key]

    __resolver: dns.resolver.Resolver

    def __init__(self, nameserver: str, port: int, zone: "Zone") -> None:
        self._nameserver = nameserver
        self._port = port
        self._zone = zone
        self._keyring = dns.tsigkeyring.from_text({zone.name: zone.tsig_key})

    @property
    def _resolver(self) -> dns.resolver.Resolver:
        if not hasattr(self, "__resolver"):
            self.__resolver = dns.resolver.Resolver()
            self.__resolver.nameservers = [self._nameserver]
            self.__resolver.port = self._port
        return self.__resolver

    def _create_update_message(self) -> dns.update.UpdateMessage:
        return dns.update.UpdateMessage(
            self._zone.name,
            keyring=self._keyring,
            keyalgorithm=dns.tsig.HMAC_SHA512,
        )

    def _query(self, message: dns.message.Message) -> dns.message.Message:
        """Catch some errors and convert this errors to dyndns specific
        errors."""
        try:
            return dns.query.tcp(
                message, where=self._nameserver, port=self._port, timeout=5
            )
        except dns.tsig.PeerBadKey:
            raise DNSServerError(
                f'The peer "{self._nameserver}" didn\'t know the tsig key '
                f'we used for the zone "{self._zone.name}".'
            )
        except dns.exception.Timeout:
            raise DNSServerError(
                f'The DNS operation to the nameserver "{self._nameserver}" timed out.'
            )

    def _normalize_name(self, name: str) -> str:
        """
        :param name: A record name (e. g. ``dyndns``) or a fully qualified
            domain name (e. g. ``dyndns.example.com``).

        :return: A fully qualified domain name (e. g. ``dyndns.example.com.``).
        """
        return self._zone.get_fqdn(name)

    def add_record(
        self, name: str, record_type: RecordType, content: str, ttl: int = 300
    ) -> DnsChangeMessage:
        """
        Add one record. All existing records with the same name and same record
        type are deleted before a new record is added.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
            domain name (e. g. ``dyndns.example.com``).
        :param record_type: The type of the resource record. ``dyndns``
            supports only ``A``, ``AAAA`` and ``TXT`` record types.
        """
        fqdn = self._normalize_name(name)
        old = self.read_record(fqdn, record_type)
        self._delete_record(fqdn, record_type)
        message: dns.update.UpdateMessage = self._create_update_message()
        message.add(fqdn, ttl, record_type, content)
        self._query(message)
        new = self.read_record(fqdn, record_type)
        return DnsChangeMessage(fqdn=fqdn, old=old, new=new, record_type=record_type)

    def read_resource_record_set(
        self, name: str, record_type: RecordType
    ) -> dns.rrset.RRset | None:
        """
        :param name: A record name (e. g. ``dyndns``) or a fully qualified
            domain name (e. g. ``dyndns.example.com``).
        :param record_type: The type of the resource record. ``dyndns``
            supports only ``A``, ``AAAA`` and ``TXT`` record types.
        """
        result: dns.resolver.Answer = self._resolver.resolve(
            self._normalize_name(name), record_type
        )
        return result.rrset

    def read_record(self, name: str, record_type: RecordType) -> str | None:
        """
        Read one record.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
            domain name (e. g. ``dyndns.example.com``).
        :param record_type: The type of the resource record. ``dyndns``
            supports only ``A``, ``AAAA`` and ``TXT`` record types.
        """
        try:
            result: Any = self.read_resource_record_set(name, record_type)
            if result and len(result) > 0:
                if record_type == "TXT":
                    element = result.pop()
                    result = element.strings[0].decode()
                    if isinstance(result, str):
                        return result
                    raise ValueError("The record could not be read.")
                else:
                    return str(result[0])
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
        return None

    def read_a_record(self, name: str) -> str | None:
        """
        Read an IPv4 address record.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
            domain name (e. g. ``dyndns.example.com``).

        :return: An IPv4 address.
        """
        return self.read_record(name, "A")

    def read_aaaa_record(self, name: str) -> str | None:
        """
        Read an IPv6 address record.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
            domain name (e. g. ``dyndns.example.com``).

        :return: An IPv6 address.
        """
        return self.read_record(name, "AAAA")

    def is_a_record(self, name: str) -> bool:
        """
        Return ``True`` if the specified name has an A record (IPv4).

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
            domain name (e. g. ``dyndns.example.com``).

        :return: `True`` if the specified name has an A record (IPv4).
        """
        return self.read_a_record(name) is not None

    def is_aaaa_record(self, name: str) -> bool:
        """
        Return ``True`` if the specified name has an AAAA record (IPv6).

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
            domain name (e. g. ``dyndns.example.com``).

        :return: `True`` if the specified name has an AAAA record (IPv6).
        """
        return self.read_aaaa_record(name) is not None

    def _delete_record(
        self, name: str, record_type: RecordType = "A"
    ) -> dns.message.Message:
        """
        Delete one record or multiple records of a specific record type.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
            domain name (e. g. ``dyndns.example.com``).
        :param record_type: The type of the resource record. ``dyndns``
            supports only ``A``, ``AAAA`` and ``TXT`` record types.
        """
        message: dns.update.UpdateMessage = self._create_update_message()
        message.delete(self._normalize_name(name), record_type)
        return self._query(message)

    def delete_record(
        self, name: str, record_type: RecordType = "A"
    ) -> DnsChangeMessage:
        """
        Delete one record or multiple records of a specific record type.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
            domain name (e. g. ``dyndns.example.com``).
        :param record_type: The type of the resource record. ``dyndns``
            supports only ``A``, ``AAAA`` and ``TXT`` record types.
        """
        fqdn: str = self._normalize_name(name)
        old = self.read_record(fqdn, record_type)
        self._delete_record(fqdn, record_type)
        return DnsChangeMessage(fqdn=fqdn, old=old, new=None, record_type=record_type)

    def delete_records(self, name: str) -> None:
        """Delete all A and the AAAA records.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
            domain name (e. g. ``dyndns.example.com``).
        """
        self._delete_record(name, "A")
        self._delete_record(name, "AAAA")

    def check(self) -> str:
        """Check the functionality of the DNS server by creating a temporary text record."""
        check_record_name = "dyndns-check-tmp-a841278b-f089-4164-b8e6-f90514e573ec"
        random_content: str = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )
        self._delete_record(check_record_name, "TXT")
        self.add_record(check_record_name, "TXT", random_content)
        result: str | None = self.read_record(check_record_name, "TXT")
        self._delete_record(check_record_name, "TXT")
        if not result:
            raise CheckError("no response")
        if result != random_content:
            raise CheckError("check failed")
        else:
            return logger.log(
                LogLevel.INFO,
                "The update check passed: "
                f"A TXT record '{check_record_name}' with the content '{random_content}' "
                f"could be updated on the zone '{self._zone.name}'.",
            )
