from jfddns import \
    load_config, \
    update_dns_record, \
    validate_args
import os
import unittest
from unittest import mock
import _helper


class TestConfig(unittest.TestCase):

    def test_config(self):
        config = load_config(os.path.join(os.path.dirname(__file__), 'files',
                             'config.yml'))
        self.assertEqual(config['secret'], 12345678)


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
            'Your configuration must have a "zones" key.'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_zones_string(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678',
                                      'nameserver': '127.0.0.1',
                                      'zones': 'lol'}),
            'Your "zones" key must contain a list of zones.'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_zones_empty_list(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678',
                                      'nameserver': '127.0.0.1',
                                      'zones': []}),
            'You must have at least one zone configured, for example:'
            '"- name: example.com" and "twig_key: tPyvZA=="'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_zone_no_name(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678',
                                      'nameserver': '127.0.0.1',
                                      'zones': [{'lol', '-'}]}),
            'Your zone dictionary must contain a key "name"'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_zone_no_tsig_key(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678',
                                      'nameserver': '127.0.0.1',
                                      'zones': [{'name', '-'}]}),
            'Your zone dictionary must contain a key "tsig_key"'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_secret_not_matches(self):
        self.assertEqual(
            update_dns_record(secret='lol'),
            'You specified a wrong secret key.'
        )


if __name__ == '__main__':
    unittest.main()
