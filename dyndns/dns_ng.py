#! /usr/bin/env python

import binascii
import random
import re
import string
import typing
from typing import Any

import dns.message
import dns.name
import dns.query
import dns.resolver
import dns.rrset
import dns.tsig
import dns.tsigkeyring
import dns.update
from dns.rdtypes.ANY.TXT import TXT

from dyndns.exceptions import CheckError, DnsNameError
from dyndns.log_ng import LogLevel, logger

if typing.TYPE_CHECKING:
    from dyndns.zones import Zone


def validate_hostname(hostname: str) -> str:
    """
    Validate the given hostname.

    :param hostname: The hostname to be validated.

    :return: The validated hostname as a string.
    """
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    if len(hostname) > 253:
        raise DnsNameError(
            'The hostname "{}..." is longer than 253 characters.'.format(hostname[:10])
        )

    labels: list[str] = hostname.split(".")

    tld: str = labels[-1]
    if re.match(r"[0-9]+$", tld):
        raise DnsNameError(
            'The TLD "{}" of the hostname "{}" must be not all-numeric.'.format(
                tld, hostname
            )
        )

    allowed: re.Pattern[str] = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    for label in labels:
        if not allowed.match(label):
            raise DnsNameError(
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
        raise DnsNameError('Invalid tsig key: "{}".'.format(tsig_key))
    try:
        dns.tsigkeyring.from_text({"tmp.org.": tsig_key})
        return tsig_key
    except binascii.Error:
        raise DnsNameError('Invalid tsig key: "{}".'.format(tsig_key))


class DnsZone:
    _nameserver: str
    """The ip address of the nameserver, for example ``127.0.0.1``."""

    _zone: "Zone"

    _keyring: dict[dns.name.Name, dns.tsig.Key]

    __resolver: dns.resolver.Resolver

    def __init__(self, nameserver: str, zone: "Zone") -> None:
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

    def read_record(self, record_name: str, rdtype: str) -> dns.rrset.RRset | None:
        result: dns.resolver.Answer = self._resolver.resolve(
            record_name + "." + self._zone.zone_name, rdtype
        )
        return result.rrset

    def check(self) -> None:
        check_record_name = "dyndns-check-tmp_a841278b-f089-4164-b8e6-f90514e573ec"
        random_content = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )
        self.delete_record(check_record_name, "TXT")
        self.add_record(check_record_name, 300, "TXT", random_content)
        rr_set = self.read_record(check_record_name, "TXT")
        self.delete_record(check_record_name, "TXT")

        if not rr_set:
            raise CheckError("no response")

        element: Any = rr_set.pop()

        if isinstance(element, TXT):
            result = element.strings[0].decode()
            if result != random_content:
                raise CheckError("check failed")
            else:
                logger.log(
                    LogLevel.INFO,
                    f"A TXT record {check_record_name} with the content {random_content} could be set.",
                )

        else:
            raise CheckError("no TXT record")
