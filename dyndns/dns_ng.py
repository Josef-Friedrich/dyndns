#! /usr/bin/env python

import binascii
import random
import re
import string
import typing
from dataclasses import dataclass
from typing import Any

import dns.exception
import dns.message
import dns.name
import dns.query
import dns.resolver
import dns.rrset
import dns.tsig
import dns.tsigkeyring
import dns.update

from dyndns.exceptions import CheckError, DnsNameError, DNSServerError
from dyndns.log import LogLevel, logger
from dyndns.types import RecordType

if typing.TYPE_CHECKING:
    from dyndns.zones import Zone


@dataclass
class DnsUpdate:
    old: str | None
    new: str | None


def validate_dns_name(name: str) -> str:
    """
    Validate the given DNS name. A dot is appended to the end of the DNS name
    if it is not already present.

    :param name: The DNS name to be validated.

    :return: The validated DNS name as a string.
    """
    if name[-1] == ".":
        # strip exactly one dot from the right, if present
        name = name[:-1]
    if len(name) > 253:
        raise DnsNameError(
            f'The DNS name "{name[:10]}..." is longer than 253 characters.'
        )

    labels: list[str] = name.split(".")

    tld: str = labels[-1]
    if re.match(r"[0-9]+$", tld):
        raise DnsNameError(
            f'The TLD "{tld}" of the DNS name "{name}" must be not all-numeric.'
        )

    allowed: re.Pattern[str] = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    for label in labels:
        if not allowed.match(label):
            raise DnsNameError(
                f'The label "{label}" of the hostname "{name}" is invalid.'
            )

    return str(dns.name.from_text(name))


def validate_tsig_key(tsig_key: str) -> str:
    """
    Validates a TSIG key.

    :param tsig_key: The TSIG key to validate.

    :return: The validated TSIG key.

    :raises NamesError: If the TSIG key is invalid.
    """
    if not tsig_key:
        raise DnsNameError(f'Invalid tsig key: "{tsig_key}".')
    try:
        dns.tsigkeyring.from_text({"tmp.org.": tsig_key})
        return tsig_key
    except binascii.Error:
        raise DnsNameError(f'Invalid tsig key: "{tsig_key}".')


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

    def delete_record(
        self, name: str, record_type: RecordType = "A"
    ) -> dns.message.Message:
        """
        Delete one record or multiple records of a specific record type.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
          domain name (e. g. ``dyndns.example.com``).
        """
        message: dns.update.UpdateMessage = self._create_update_message()
        message.delete(self._normalize_name(name), record_type)
        return self._query(message)

    def delete_records(self, name: str) -> None:
        """Delete all A and the AAAA records.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
          domain name (e. g. ``dyndns.example.com``).
        """
        self.delete_record(name, "A")
        self.delete_record(name, "AAAA")

    def add_record(
        self, name: str, record_type: RecordType, content: str, ttl: int = 300
    ) -> DnsUpdate:
        """
        Add one record. All existing records with the same name and same record
        type are deleted before a new record is added.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
          domain name (e. g. ``dyndns.example.com``).
        """
        old_content = self.read_record(name, record_type)
        self.delete_record(name, record_type)
        message: dns.update.UpdateMessage = self._create_update_message()
        message.add(self._normalize_name(name), ttl, record_type, content)
        self._query(message)
        new_content = self.read_record(name, record_type)
        return DnsUpdate(old=old_content, new=new_content)

    def read_record(self, name: str, record_type: RecordType) -> str | None:
        """
        Read one record.

        :param name: A record name (e. g. ``dyndns``) or a fully qualified
          domain name (e. g. ``dyndns.example.com``).
        """
        try:
            result: Any = self._resolver.resolve(
                self._normalize_name(name), record_type
            )
            if result and len(result) > 0:
                if record_type == "TXT":
                    element = result.rrset.pop()
                    return element.strings[0].decode()
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

    def check(self) -> str:
        """Check the functionality of the DNS server by creating a temporary text record."""
        check_record_name = "dyndns-check-tmp_a841278b-f089-4164-b8e6-f90514e573ec"
        random_content: str = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )
        self.delete_record(check_record_name, "TXT")
        self.add_record(check_record_name, "TXT", random_content)
        result: str | None = self.read_record(check_record_name, "TXT")
        self.delete_record(check_record_name, "TXT")
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
