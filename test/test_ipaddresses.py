from dyndns.ipaddresses import IpAddresses
from dyndns.exceptions import IpAddressesError
import unittest


class TestClassIpAddresses(unittest.TestCase):

    def assertRaisesMsg(self, kwargs, msg):
        with self.assertRaises(IpAddressesError) as cm:
            IpAddresses(**kwargs)
        self.assertEqual(str(cm.exception), msg)

    def test_invalid_ipv4(self):
        self.assertRaisesMsg({'ipv4': 'lol'}, 'Invalid ip address "lol"')

    def test_invalid_ipv4_version(self):
        self.assertRaisesMsg(
            {'ipv4': '1::2'},
            'IP version "4" does not match.'
        )

    def test_invalid_ipv6(self):
        self.assertRaisesMsg({'ipv6': 'lol'}, 'Invalid ip address "lol"')

    def test_invalid_ipv6_version(self):
        self.assertRaisesMsg(
            {'ipv6': '1.2.3.4'},
            'IP version "6" does not match.'
        )

    def test_no_ip(self):
        self.assertRaisesMsg({}, 'No ip address set.')

    def test_two_ipv4(self):
        self.assertRaisesMsg(
            {'ip_1': '1.2.3.4', 'ip_2': '1.2.3.5'},
            'The attribute "ipv4" is already set and has the value "1.2.3.4".',
        )

    def test_two_ipv6(self):
        self.assertRaisesMsg(
            {'ip_1': '1::2', 'ip_2': '1::3'},
            'The attribute "ipv6" is already set and has the value "1::2".',
        )

    def test_valid_ipv4(self):
        ips = IpAddresses(ipv4='1.2.3.4')
        self.assertEqual(ips.ipv4, '1.2.3.4')

    def test_valid_ipv4_set_1(self):
        ips = IpAddresses(ip_1='1.2.3.4')
        self.assertEqual(ips.ipv4, '1.2.3.4')

    def test_valid_ipv4_set_2(self):
        ips = IpAddresses(ip_2='1.2.3.4')
        self.assertEqual(ips.ipv4, '1.2.3.4')

    def test_valid_ipv6(self):
        ips = IpAddresses(ipv6='1::2')
        self.assertEqual(ips.ipv6, '1::2')

    def test_valid_ipv6_set_1(self):
        ips = IpAddresses(ip_1='1::2')
        self.assertEqual(ips.ipv6, '1::2')

    def test_valid_ipv6_set_2(self):
        ips = IpAddresses(ip_2='1::2')
        self.assertEqual(ips.ipv6, '1::2')

    def test_valid_ipv4_ipv6(self):
        ips = IpAddresses(ipv4='1.2.3.4', ipv6='1::2')
        self.assertEqual(ips.ipv4, '1.2.3.4')
        self.assertEqual(ips.ipv6, '1::2')


if __name__ == '__main__':
    unittest.main()
