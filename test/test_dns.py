from jfddns.dns import DnsUpdate, Zones
import _helper
import unittest
import ipaddress
from unittest import mock


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

    def test_method_build_tsigkeyring(self):
        du = DnsUpdate('127.0.0.1', 'example.com', 'tPyvZA==')
        result = du._build_tsigkeyring(du._zone, du.tsig_key)
        for zone, tsig_key in result.items():
            self.assertEqual(str(zone), 'example.com.')
            self.assertEqual(tsig_key, b'\xb4\xfc\xafd')

    def test_method_convert_record_type(self):
        self.assertEqual(DnsUpdate._convert_record_type(4), 'a')
        self.assertEqual(DnsUpdate._convert_record_type(6), 'aaaa')

    def test_method_build_fqdn(self):
        dns = DnsUpdate('127.0.0.1', 'example.com', 'tPyvZA==')
        self.assertEqual(str(dns._build_fqdn('lol')), 'lol.example.com.')

    @unittest.skipIf(NO_INTERNET_CONNECTIFITY, 'No uplink')
    def test_method_resolve_unpatched(self):
        dns = DnsUpdate('8.8.8.8', 'google.com.', 'tPyvZA==')
        ip = dns._resolve('www', 4)
        ipaddress.ip_address(ip)

    @mock.patch('dns.resolver.Resolver')
    def test_method_resolve_patched(self, Resolver):
        resolver = Resolver.return_value
        resolver.query.return_value = ['1.2.3.4']
        dns = DnsUpdate('8.8.8.8', 'google.com.', 'tPyvZA==')
        ip = dns._resolve('www', 4)
        ipaddress.ip_address(ip)
        self.assertEqual(ip, '1.2.3.4')

    @mock.patch('dns.query.tcp')
    @mock.patch('dns.resolver.Resolver')
    def test_method_set_record(self, Resolver, tcp):
        resolver = Resolver.return_value
        resolver.query.return_value = ['1.2.3.4']
        dns = DnsUpdate('127.0.0.1', 'example.com', 'tPyvZA==')
        dns.record_name = 'www'
        dns._set_record('1.2.3.5', 4)
        args, kwargs = tcp.call_args
        messages, nameserver = args
        self.assertEqual(str(messages.question[0]), 'example.com. IN SOA')
        self.assertEqual(nameserver, '127.0.0.1')
