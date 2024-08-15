"""Deal with ipv4 and ipv6 IP addresses."""

from __future__ import annotations

import ipaddress
from typing import Any, Literal

from flask import Request

from dyndns.exceptions import IpAddressesError


def validate(
    address: Any, ip_version: Literal[4, 6] | None = None
) -> tuple[str, Literal[4, 6]]:
    try:
        address = ipaddress.ip_address(address)
        if ip_version and ip_version != address.version:
            raise IpAddressesError(f'IP version "{ip_version}" does not match.')
        return str(address), address.version
    except ValueError:
        raise IpAddressesError(f'Invalid ip address "{address}"')


def format_attr(ip_version: Literal[4, 6]) -> str:
    return f"ipv{ip_version}"


class IpAddressContainer:
    """
    A container class to store and detect IP addresses in both versions
    (ipv4 and ipv6).

    :param str ip_1: An IP address of unkown version.
    :param str ip_2: An IP address of unkown version.
    :param str ipv4: An ipv4 IP address.
    :param str ipv6: An ipv6 IP address.
    """

    ipv4: str | None
    """The ipv4 address to update the DNS record with."""

    ipv6: str | None
    """The ipv6 address to update the DNS record with."""

    request: Request

    def __init__(
        self,
        ip_1: str | None = None,
        ip_2: str | None = None,
        ipv4: str | None = None,
        ipv6: str | None = None,
        request: Request | None = None,
    ) -> None:
        if request:
            self.request = request

        self.ipv4 = None
        if ipv4:
            self.ipv4, _ = validate(ipv4, 4)

        self.ipv6 = None
        if ipv6:
            self.ipv6, _ = validate(ipv6, 6)

        if ip_1:
            self._set_ip(ip_1)

        if ip_2:
            self._set_ip(ip_2)

        if not self.ipv4 and not self.ipv6:
            self._get_client_ip()

        if not self.ipv4 and not self.ipv6:
            raise IpAddressesError("No ip address set.")

    def _get_ip(self, ip_version: Literal[4, 6]) -> str:
        return getattr(self, format_attr(ip_version))

    def _setattr(self, ip_version: Literal[4, 6], value: str) -> None:
        return setattr(self, format_attr(ip_version), value)

    def _get_client_ip(self) -> str | None:
        # request.environ['REMOTE_ADDR']
        if hasattr(self, "request"):
            remote_addr: str | None = self.request.remote_addr
            if remote_addr:
                self._set_ip(remote_addr)
                return remote_addr
        return None

    def _set_ip(self, address: str) -> None:
        ip, ip_version = validate(address)
        old_ip: str = self._get_ip(ip_version)
        if old_ip:
            msg: str = f'The attribute "{format_attr(ip_version)}" is already set and has the value "{old_ip}".'
            raise IpAddressesError(msg)

        self._setattr(ip_version, ip)
