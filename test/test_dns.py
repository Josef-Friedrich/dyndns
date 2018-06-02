from jfddns.dns import DnsUpdate, split_fqdn
import _helper
import unittest
import ipaddress


NO_INTERNET_CONNECTIFITY = not _helper.check_internet_connectifity()


class TestClassDnsUpdate(unittest.TestCase):

    def test_method_convert_record_type(self):
        self.assertEqual(DnsUpdate._convert_record_type(4), 'a')
        self.assertEqual(DnsUpdate._convert_record_type(6), 'aaaa')

    def test_method_concatenate(self):
        dns = DnsUpdate('ns.example.com', 'example.com', 'tPyvZA==')
        self.assertEqual(str(dns._concatenate('lol')), 'lol.example.com.')

    @unittest.skipIf(NO_INTERNET_CONNECTIFITY, 'No uplink')
    def test_resolver(self):
        dns = DnsUpdate('8.8.8.8', 'google.com.', 'tPyvZA==')
        ip = dns._resolve('www', 4)
        ipaddress.ip_address(ip)


class TestFunctionSplitHostname(unittest.TestCase):

    zones = [
        {'zone': 'example.com.'},
        {'zone': 'example.org'},
    ]

    def test_with_dot(self):
        result = split_fqdn('www.example.com', self.zones)
        self.assertEqual(result, ('www.', 'example.com.'))

    def test_with_org(self):
        result = split_fqdn('www.example.org', self.zones)
        self.assertEqual(result, ('www.', 'example.org.'))

    def test_unkown_zone(self):
        result = split_fqdn('www.xx.org', self.zones)
        self.assertEqual(result, None)
