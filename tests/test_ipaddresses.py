import unittest

import pytest

from dyndns.exceptions import IpAddressesError
from dyndns.ipaddresses import IpAddressContainer


class TestClassIpAddresses:
    def assert_raises_msg(self, kwargs, msg):
        with pytest.raises(IpAddressesError) as e:
            IpAddressContainer(**kwargs)
        assert e.value.args[0] == msg

    def test_invalid_ipv4(self):
        self.assert_raises_msg({"ipv4": "lol"}, 'Invalid ip address "lol"')

    def test_invalid_ipv4_version(self):
        self.assert_raises_msg({"ipv4": "1::2"}, 'IP version "4" does not match.')

    def test_invalid_ipv6(self):
        self.assert_raises_msg({"ipv6": "lol"}, 'Invalid ip address "lol"')

    def test_invalid_ipv6_version(self):
        self.assert_raises_msg({"ipv6": "1.2.3.4"}, 'IP version "6" does not match.')

    def test_no_ip(self):
        self.assert_raises_msg({}, "No ip address set.")

    def test_two_ipv4(self):
        self.assert_raises_msg(
            {"ip_1": "1.2.3.4", "ip_2": "1.2.3.5"},
            'The attribute "ipv4" is already set and has the value "1.2.3.4".',
        )

    def test_two_ipv6(self):
        self.assert_raises_msg(
            {"ip_1": "1::2", "ip_2": "1::3"},
            'The attribute "ipv6" is already set and has the value "1::2".',
        )

    def test_valid_ipv4(self):
        ips = IpAddressContainer(ipv4="1.2.3.4")
        assert ips.ipv4 == "1.2.3.4"

    def test_valid_ipv4_set_1(self):
        ips = IpAddressContainer(ip_1="1.2.3.4")
        assert ips.ipv4 == "1.2.3.4"

    def test_valid_ipv4_set_2(self):
        ips = IpAddressContainer(ip_2="1.2.3.4")
        assert ips.ipv4 == "1.2.3.4"

    def test_valid_ipv6(self):
        ips = IpAddressContainer(ipv6="1::2")
        assert ips.ipv6 == "1::2"

    def test_valid_ipv6_set_1(self):
        ips = IpAddressContainer(ip_1="1::2")
        assert ips.ipv6 == "1::2"

    def test_valid_ipv6_set_2(self):
        ips = IpAddressContainer(ip_2="1::2")
        assert ips.ipv6 == "1::2"

    def test_valid_ipv4_ipv6(self):
        ips = IpAddressContainer(ipv4="1.2.3.4", ipv6="1::2")
        assert ips.ipv4 == "1.2.3.4"
        assert ips.ipv6 == "1::2"


if __name__ == "__main__":
    unittest.main()
