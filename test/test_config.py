from dyndns.config import validate_config, load_config, validate_secret
from dyndns.exceptions import ConfigurationError
import os
import unittest
from unittest import mock
import _helper


class TestConfig(unittest.TestCase):

    def test_config(self):
        os.environ['dyndns_CONFIG_FILE'] = _helper.config_file
        config = load_config()
        self.assertEqual(config['secret'], 12345678)


class TestFunctionValidateSecret(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(validate_secret('abcd1234'), 'abcd1234')

    def test_invalid_to_short(self):
        with self.assertRaises(ConfigurationError):
            validate_secret('1234567')

    def test_invalid_non_alpanumeric(self):
        with self.assertRaises(ConfigurationError):
            validate_secret('12345äüö')


class TestFunctionValidateConfig(unittest.TestCase):

    def setUp(self):
        os.environ['dyndns_CONFIG_FILE'] = _helper.config_file

    def assertRaisesMsg(self, config, msg):
        with self.assertRaises(ConfigurationError) as cm:
            validate_config(config)

        self.assertEqual(str(cm.exception), msg)

    @mock.patch('os.path.exists')
    def test_no_config_file(self, exists):
        exists.return_value = False
        os.environ['dyndns_CONFIG_FILE'] = '/tmp/dyndns-xxx.yml'
        self.assertRaisesMsg(
            None,
            'The configuration file could not be found.',
        )

    def test_invalid_yaml_format(self):
        config_file = os.path.join(_helper.files_dir, 'invalid-yaml.yml')
        os.environ['dyndns_CONFIG_FILE'] = config_file
        self.assertRaisesMsg(
            None,
            'The configuration file is in a invalid YAML format.',
        )

    def test_no_secret(self):
        self.assertRaisesMsg(
            {'lol': 'lol'},
            'Your configuration must have a "secret" key, for example: '
            '"secret: VDEdxeTKH"'
        )

    def test_invalid_secret(self):
        self.assertRaisesMsg(
            {'secret': 'ä'},
            'The secret must be at least 8 characters long and may not '
            'contain any non-alpha-numeric characters.'
        )

    def test_no_nameserver(self):
        self.assertRaisesMsg(
            {'secret': '12345678'},
            'Your configuration must have a "nameserver" key, '
            'for example: "nameserver: 127.0.0.1"'
        )

    def test_invalid_nameserver_ip(self):
        self.assertRaisesMsg(
            {'secret': '12345678', 'nameserver': 'lol'},
            'The "nameserver" entry in your configuration is not a valid IP '
            'address: "lol".'
        )

    def test_invalid_dyndns_domain(self):
        self.assertRaisesMsg(
            {'secret': '12345678', 'nameserver': '127.0.0.1',
             'dyndns_domain': 'l o l'},
            'The label "l o l" of the hostname "l o l" is invalid.'
        )

    def test_no_zones(self):
        self.assertRaisesMsg(
            {'secret': '12345678', 'nameserver': '127.0.0.1'},
            'Your configuration must have a "zones" key.'
        )

    def test_zones_string(self):
        self.assertRaisesMsg(
            {'secret': '12345678', 'nameserver': '127.0.0.1',
             'zones': 'lol'},
            'Your "zones" key must contain a list of zones.'
        )

    def test_zones_empty_list(self):
        self.assertRaisesMsg(
            {'secret': '12345678', 'nameserver': '127.0.0.1',
             'zones': []},
            'You must have at least one zone configured, for example: '
            '"- name: example.com" and "tsig_key: tPyvZA=="'
        )

    def test_zone_no_name(self):
        self.assertRaisesMsg(
            {'secret': '12345678', 'nameserver': '127.0.0.1',
             'zones': [{'lol': '-'}]},
            'Your zone dictionary must contain a key "name"'
        )

    def test_zone_invalid_zone_name(self):
        config = {'secret': '12345678', 'nameserver': '127.0.0.1',
                  'zones': [{'name': 'l o l', 'tsig_key': 'xxx'}]}
        self.assertRaisesMsg(
            config,
            'The label "l o l" of the hostname "l o l" is invalid.',
        )

    def test_zone_no_tsig_key(self):
        self.assertRaisesMsg(
            {'secret': '12345678', 'nameserver': '127.0.0.1',
             'zones': [{'name': 'a'}]},
            'Your zone dictionary must contain a key "tsig_key"'
        )

    def test_zone_invalid_tsig_key(self):
        config = {'secret': '12345678', 'nameserver': '127.0.0.1',
                  'zones': [{'name': 'a', 'tsig_key': 'xxx'}]}
        self.assertRaisesMsg(
            config,
            'Invalid tsig key: "xxx".',
        )

    def test_valid(self):
        config = load_config()
        config = validate_config(config)
        self.assertEqual(config['secret'], '12345678')
        self.assertEqual(config['dyndns_domain'], 'example.com')


if __name__ == '__main__':
    unittest.main()
