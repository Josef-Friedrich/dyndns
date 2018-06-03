from jfddns.dns import DnsUpdate, Zones
import _helper
import unittest
import ipaddress


NO_INTERNET_CONNECTIFITY = not _helper.check_internet_connectifity()


class TestClassZones(unittest.TestCase):

    def test_init(self):
        zones = Zones([{'name': 'example.org', 'tsig_key': 'tPyvZA=='}])
        self.assertEqual(zones.zones[0]['example.org.'], 'tPyvZA==')


class TestClassZonesMethodSplitFqdn(unittest.TestCase):

    zones = Zones([
        {'name': 'example.com.', 'tsig_key': 'tPyvZA=='},
        {'name': 'example.org', 'tsig_key': 'tPyvZA=='},
    ])

    def test_with_dot(self):
        result = self.zones.split_fqdn('www.example.com')
        self.assertEqual(result, ('www.', 'example.com.'))

    def test_with_org(self):
        result = self.zones.split_fqdn('www.example.org')
        self.assertEqual(result, ('www.', 'example.org.'))

    def test_unkown_zone(self):
        result = self.zones.split_fqdn('www.xx.org')
        self.assertEqual(result, None)


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
