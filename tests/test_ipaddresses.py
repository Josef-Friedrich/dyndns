from typing import TypedDict

import pytest
from pydantic import BaseModel, ValidationError

from dyndns.exceptions import IpAddressesError
from dyndns.ipaddresses import IpAddress, IpAddressContainer


class IpAddressContainerKwargs(TypedDict, total=False):
    ip_1: str
    ip_2: str
    ipv4: str
    ipv6: str


class Ip(BaseModel):
    ip: IpAddress


class TestAnnotatedIpAdress:
    def test_valid(self) -> None:
        ip = Ip(ip="1.2.3.4")
        assert ip.ip == "1.2.3.4"

    def test_invalid(self) -> None:
        with pytest.raises(ValidationError):
            Ip(ip="Invalid")


class TestClassIpAddresses:
    def assert_raises_msg(self, kwargs: IpAddressContainerKwargs, message: str) -> None:
        with pytest.raises(IpAddressesError, match=message):
            IpAddressContainer(**kwargs)

    def test_invalid_ipv4(self) -> None:
        self.assert_raises_msg({"ipv4": "test"}, "Invalid IP address 'test'.")

    def test_invalid_ipv4_version(self) -> None:
        self.assert_raises_msg({"ipv4": "1::2"}, 'IP version "4" does not match.')

    def test_invalid_ipv6(self) -> None:
        self.assert_raises_msg({"ipv6": "test"}, "Invalid IP address 'test'.")

    def test_invalid_ipv6_version(self) -> None:
        self.assert_raises_msg({"ipv6": "1.2.3.4"}, 'IP version "6" does not match.')

    def test_no_ip(self) -> None:
        self.assert_raises_msg({}, "No ip address set.")

    def test_two_ipv4(self) -> None:
        self.assert_raises_msg(
            {"ip_1": "1.2.3.4", "ip_2": "1.2.3.5"},
            'The attribute "ipv4" is already set and has the value "1.2.3.4".',
        )

    def test_two_ipv6(self) -> None:
        self.assert_raises_msg(
            {"ip_1": "1::2", "ip_2": "1::3"},
            'The attribute "ipv6" is already set and has the value "1::2".',
        )

    def test_valid_ipv4(self) -> None:
        ips = IpAddressContainer(ipv4="1.2.3.4")
        assert ips.ipv4 == "1.2.3.4"

    def test_valid_ipv4_set_1(self) -> None:
        ips = IpAddressContainer(ip_1="1.2.3.4")
        assert ips.ipv4 == "1.2.3.4"

    def test_valid_ipv4_set_2(self) -> None:
        ips = IpAddressContainer(ip_2="1.2.3.4")
        assert ips.ipv4 == "1.2.3.4"

    def test_valid_ipv6(self) -> None:
        ips = IpAddressContainer(ipv6="1::2")
        assert ips.ipv6 == "1::2"

    def test_valid_ipv6_set_1(self) -> None:
        ips = IpAddressContainer(ip_1="1::2")
        assert ips.ipv6 == "1::2"

    def test_valid_ipv6_set_2(self) -> None:
        ips = IpAddressContainer(ip_2="1::2")
        assert ips.ipv6 == "1::2"

    def test_valid_ipv4_ipv6(self) -> None:
        ips = IpAddressContainer(ipv4="1.2.3.4", ipv6="1::2")
        assert ips.ipv4 == "1.2.3.4"
        assert ips.ipv6 == "1::2"
