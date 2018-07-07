from dyndns.dns import DnsUpdate
import _helper
import unittest
import ipaddress
from unittest import mock
from dyndns.ipaddresses import IpAddresses
from dyndns.names import Names
import copy

ipaddresses = IpAddresses(ipv4='1.2.3.4')
zones = _helper.zones
names = Names(zones, fqdn='www.example.com')

NO_INTERNET_CONNECTIFITY = not _helper.check_internet_connectifity()


class TestClassDnsUpdate(unittest.TestCase):

    def test_method_build_tsigkeyring(self):
        du = DnsUpdate('127.0.0.1', names, ipaddresses)
        result = du._build_tsigkeyring(du.names.zone_name, du.names.tsig_key)
        for zone, tsig_key in result.items():
            self.assertEqual(str(zone), 'example.com.')
            self.assertEqual(tsig_key, b'\xb4\xfc\xafd')

    def test_method_convert_record_type(self):
        self.assertEqual(DnsUpdate._convert_record_type(4), 'a')
        self.assertEqual(DnsUpdate._convert_record_type(6), 'aaaa')

    @unittest.skipIf(NO_INTERNET_CONNECTIFITY, 'No uplink')
    def test_method_resolve_unpatched(self):
        _names = copy.deepcopy(names)
        _names.zone_name = 'google.com.'
        dns = DnsUpdate('8.8.8.8', _names, ipaddresses)
        ip = dns._resolve(4)
        ipaddress.ip_address(ip)

    @mock.patch('dns.resolver.Resolver')
    def test_method_resolve_patched(self, Resolver):
        resolver = Resolver.return_value
        resolver.query.return_value = ['1.2.3.4']
        dns = DnsUpdate('8.8.8.8', names, ipaddresses)
        ip = dns._resolve(4)
        ipaddress.ip_address(ip)
        self.assertEqual(ip, '1.2.3.4')

    @mock.patch('dns.query.tcp')
    @mock.patch('dns.update.Update')
    @mock.patch('dns.resolver.Resolver')
    def test_method_set_record_updated(self, Resolver, Update, tcp):
        resolver = Resolver.return_value
        resolver.query.side_effect = [['1.2.3.4'], ['1.2.3.5']]
        update = Update.return_value

        dns = DnsUpdate('127.0.0.1', names, ipaddresses)
        dns.record_name = 'www'
        result = dns._set_record('1.2.3.5', 4)

        update.delete.assert_has_calls([
            mock.call('www.example.com.', 'a'),
            mock.call('www.example.com.', 'aaaa'),
        ])
        update.add.assert_called_with('www.example.com.', 300, 'a', '1.2.3.5')
        self.assertEqual(tcp.call_args[1]['where'], '127.0.0.1')
        Update.assert_called()

        self.assertEqual(
            result,
            {'ip_version': 4, 'new_ip': '1.2.3.5', 'old_ip': '1.2.3.4',
             'status': 'UPDATED'},
        )

    @mock.patch('dns.query.tcp')
    @mock.patch('dns.update.Update')
    @mock.patch('dns.resolver.Resolver')
    def test_method_set_record_unchanged(self, Resolver, Update, tcp):
        resolver = Resolver.return_value
        resolver.query.return_value = ['1.2.3.4']
        update = Update.return_value

        dns = DnsUpdate('127.0.0.1', names, ipaddresses)
        dns.record_name = 'www'
        result = dns._set_record('1.2.3.4', 4)

        update.delete.assert_not_called()
        update.add.assert_not_called()

        self.assertEqual(
            result,
            {'ip_version': 4, 'new_ip': '1.2.3.4', 'old_ip': '1.2.3.4',
             'status': 'UNCHANGED'},
        )

    @mock.patch('dns.query.tcp')
    @mock.patch('dns.update.Update')
    @mock.patch('dns.resolver.Resolver')
    def test_method_set_record_error(self, Resolver, Update, tcp):
        resolver = Resolver.return_value
        resolver.query.return_value = ['1.2.3.4']

        dns = DnsUpdate('127.0.0.1', names, ipaddresses)
        dns.record_name = 'www'
        result = dns._set_record('1.2.3.5', 4)

        self.assertEqual(
            result,
            {'ip_version': 4, 'new_ip': '1.2.3.5', 'old_ip': '1.2.3.4',
             'status': 'DNS_SERVER_ERROR'},
        )
