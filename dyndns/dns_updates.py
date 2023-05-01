"""Interface for DNS updates."""

from __future__ import annotations

from typing import Any

import flask

from dyndns.config import Config, get_config
from dyndns.dns import DnsUpdate
from dyndns.exceptions import (
    ConfigurationError,
    DNSServerError,
    IpAddressesError,
    NamesError,
    ParameterError,
)
from dyndns.ipaddresses import IpAddressContainer
from dyndns.log import msg
from dyndns.names import Names
from dyndns.types import UpdateRecord


def authenticate(secret: Any, config: Config):
    if str(secret) != str(config["secret"]):
        raise ParameterError("You specified a wrong secret key.")


def raise_parameter_error(function, exception, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except exception as e:
        raise ParameterError(str(e))


def update_dns_record(
    secret: str | None = None,
    fqdn: str | None = None,
    zone_name: str | None = None,
    record_name: str | None = None,
    ip_1: str | None = None,
    ip_2: str | None = None,
    ipv4: str | None = None,
    ipv6: str | None = None,
    ttl: int | None = None,
    config: Config | None = None,
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

    if not config:
        config = get_config()

    zones = config["zones"]

    authenticate(secret, config)

    names = raise_parameter_error(
        Names,
        NamesError,
        zones,
        fqdn=fqdn,
        zone_name=zone_name,
        record_name=record_name,
    )
    ip_addresses = raise_parameter_error(
        IpAddressContainer,
        IpAddressesError,
        ip_1=ip_1,
        ip_2=ip_2,
        ipv4=ipv4,
        ipv6=ipv6,
        request=flask.request,
    )

    update = DnsUpdate(
        nameserver=config["nameserver"],
        names=names,
        ipaddresses=ip_addresses,
        ttl=ttl,
    )
    results: list[UpdateRecord] = update.update()

    messages: list[str] = []
    for result in results:
        message = "fqdn: {} old_ip: {} new_ip: {}".format(
            names.fqdn,
            result["old_ip"],
            result["new_ip"],
        )
        messages.append(msg(message, result["status"]))

    return "".join(messages)


def delete_dns_record(
    secret: str | None = None, fqdn: str | None = None, config: Config | None = None
):
    if not config:
        config = get_config()
    zones = config["zones"]

    authenticate(secret, config)

    names = raise_parameter_error(Names, NamesError, zones, fqdn=fqdn)

    delete = DnsUpdate(
        nameserver=config["nameserver"],
        names=names,
    )

    if delete.delete():
        return msg('Deleted "{}".'.format(names.fqdn), "UPDATED")
    return msg('Deletion not successful "{}".'.format(names.fqdn), "UNCHANGED")


def catch_errors(function, **kwargs):
    try:
        return function(**kwargs)
    except ParameterError as error:
        return msg(str(error), "PARAMETER_ERROR")
    except ConfigurationError as error:
        return msg(str(error), "CONFIGURATION_ERROR")
    except DNSServerError as error:
        return msg(str(error), "DNS_SERVER_ERROR")
