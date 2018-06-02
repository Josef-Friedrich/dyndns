from jfddns import \
    DnsUpdate, \
    load_config, \
    split_hostname, \
    update_dns_record, \
    validate_args, \
    Validate
import ipaddress
import os
import unittest
import socket
from unittest import mock
import _helper


def check_internet_connectifity(host="8.8.8.8", port=53, timeout=3):
    """
    https://stackoverflow.com/a/33117579
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False


NO_INTERNET_CONNECTIFITY = not check_internet_connectifity()


class TestConfig(unittest.TestCase):

    def test_config(self):
        config = load_config(os.path.join(os.path.dirname(__file__), 'files',
                             'config.yml'))
        self.assertEqual(config['secret'], 12345678)


class TestValidate(unittest.TestCase):

    def setUp(self):
        self.v = Validate()

    def test_secret_valid(self):
        self.assertEqual(self.v.secret('abcd1234'), 'abcd1234')

    def test_secret_invalid_to_short(self):
        self.assertEqual(self.v.secret('1234567'), False)

    def test_secret_invalid_non_alpanumeric(self):
        self.assertEqual(self.v.secret('12345äüö'), False)

    def test_ipv4_valid(self):
        self.assertEqual(str(self.v.ipv4('192.168.2.3')), '192.168.2.3')

    def test_ipv4_invalid_string(self):
        self.assertFalse(self.v.ipv4('lol'))

    def test_ipv4_invalid_ipv6(self):
        self.assertFalse(self.v.ipv4('1::2'))

    def test_ipv6_valid(self):
        self.assertEqual(str(self.v.ipv6('1::2')), '1::2')

    def test_ipv6_invalid_string(self):
        self.assertFalse(self.v.ipv6('lol'))

    def test_ipv6_invalid_ipv6(self):
        self.assertFalse(self.v.ipv6('1.2.3.4'))

    def test_zone_valid(self):
        self.assertEqual(self.v.zone('github.com'), 'github.com')

    def test_record_valid(self):
        self.assertEqual(self.v.record('sub'), 'sub')


class TestFunctionValidateArgs(unittest.TestCase):

    def test_empty_dict(self):
        self.assertEqual(
            validate_args({}, {}),
            {'message': 'The arguments “record”, “zone” and “secret” are '
                        'required.'}
        )

    def test_no_ip(self):
        self.assertEqual(
            validate_args({'record': '1', 'zone': '2', 'secret': '3'}, {}),
            {'message': 'The argument “ipv4” or the argument “ipv6” is '
                        'required.'}

        )

    def test_wrong_secret(self):
        self.assertEqual(
            validate_args(
                {'record': '1', 'zone': '2', 'secret': '3', 'ipv6': '1::2'},
                {'secret': '4'}),
            {'message': 'You specified a wrong secret key.'}
        )

    def test_invalid_ipv4(self):
        self.assertEqual(
            validate_args(
                {'record': 'a', 'zone': 'b', 'secret': '3', 'ipv4': '1::2'},
                {'secret': '3'}),
            {'message': 'Invalid ipv4 address.'}
        )

    def test_invalid_ipv6(self):
        self.assertEqual(
            validate_args(
                {'record': 'a', 'zone': 'b', 'secret': '3', 'ipv6': 'xxx'},
                {'secret': '3'}),
            {'message': 'Invalid ipv6 address.'}
        )

    def test_invalid_zone(self):
        self.assertEqual(
            validate_args(
                {'record': 'a', 'zone': 'b b ', 'secret': '3', 'ipv6': '1::2'},
                {'secret': '3'}),
            {'message': 'Invalid zone string.'}
        )

    def test_invalid_record(self):
        self.assertEqual(
            validate_args(
                {'record': 'a a', 'zone': 'b', 'secret': '3', 'ipv6': '1::2'},
                {'secret': '3'}),
            {'message': 'Invalid record string.'}
        )

    def test_valid(self):
        self.assertEqual(
            validate_args(
                {'record': 'a', 'zone': 'b', 'secret': '3', 'ipv6': '1::2'},
                {'secret': '3'}),
            {'ipv4': None, 'ipv6': '1::2', 'record': 'a', 'zone': 'b'}
        )


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
        result = split_hostname('www.example.com', self.zones)
        self.assertEqual(result, ('www.', 'example.com.'))

    def test_with_org(self):
        result = split_hostname('www.example.org', self.zones)
        self.assertEqual(result, ('www.', 'example.org.'))

    def test_unkown_zone(self):
        result = split_hostname('www.xx.org', self.zones)
        self.assertEqual(result, None)


class TestFunctionUpdateDnsRecord(unittest.TestCase):

    @mock.patch('jfddns.config_file', '/tmp/jfddns-xxx.yml')
    def test_no_config_file(self):
        self.assertEqual(update_dns_record(), 'The configuration file '
                         '/tmp/jfddns-xxx.yml could not be found.')

    @mock.patch('jfddns.config_file', os.path.join(_helper.files_dir,
                'invalid-yaml.yml'))
    def test_config_invalid_yaml_format(self):
        self.assertEqual(update_dns_record(), 'The configuration file is in '
                         'a invalid YAML format.')

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_no_secret(self):
        self.assertEqual(
            update_dns_record(config={'lol': 'lol'}),
            'Your configuration must have a "secret" key, for example: '
            '"secret: VDEdxeTKH"'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_invalid_secret(self):
        self.assertEqual(
            update_dns_record(config={'secret': 'ä'}),
            'The secret must be at least 8 characters long and may not '
            'contain any non-alpha-numeric characters.'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_no_nameserver(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678'}),
            'Your configuration must have a "nameserver" key, '
            'for example: "nameserver: 127.0.0.1"'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_no_zones(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678',
                                      'nameserver': '127.0.0.1'}),
            'You must have at least one zone configured, for example:'
            '"- name: example.com" and "twig_key: tPyvZA=="'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_secret_not_matches(self):
        self.assertEqual(
            update_dns_record(secret='lol'),
            'You specified a wrong secret key.'
        )


if __name__ == '__main__':
    unittest.main()
