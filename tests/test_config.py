import os
import unittest
from unittest import mock

import _helper
import pytest

from dyndns.config import load_config, validate_config, validate_secret
from dyndns.exceptions import ConfigurationError


class TestConfig:
    def test_config(self):
        os.environ["dyndns_CONFIG_FILE"] = _helper.config_file
        config = load_config()
        assert config["secret"] == 12345678


class TestFunctionValidateSecret:
    def test_valid(self):
        assert validate_secret("abcd1234") == "abcd1234"

    def test_invalid_to_short(self):
        with pytest.raises(ConfigurationError):
            validate_secret("1234567")

    def test_invalid_non_alpanumeric(self):
        with pytest.raises(ConfigurationError):
            validate_secret("12345äüö")


class TestFunctionValidateConfig:
    def setup_method(self):
        os.environ["dyndns_CONFIG_FILE"] = _helper.config_file

    def assert_raises_msg(self, config, msg: str) -> None:
        with pytest.raises(ConfigurationError) as e:
            validate_config(config)
        assert e.value.args[0] == msg

    @mock.patch("os.path.exists")
    def test_no_config_file(self, exists):
        exists.return_value = False
        os.environ["dyndns_CONFIG_FILE"] = "/tmp/dyndns-xxx.yml"
        self.assert_raises_msg(
            None,
            "The configuration file could not be found.",
        )

    def test_invalid_yaml_format(self):
        config_file = os.path.join(_helper.files_dir, "invalid-yaml.yml")
        os.environ["dyndns_CONFIG_FILE"] = config_file
        self.assert_raises_msg(
            None,
            "The configuration file is in a invalid YAML format.",
        )

    def test_no_secret(self):
        self.assert_raises_msg(
            {"lol": "lol"},
            'Your configuration must have a "secret" key, for example: '
            '"secret: VDEdxeTKH"',
        )

    def test_invalid_secret(self):
        self.assert_raises_msg(
            {"secret": "ä"},
            "The secret must be at least 8 characters long and may not "
            "contain any non-alpha-numeric characters.",
        )

    def test_no_nameserver(self):
        self.assert_raises_msg(
            {"secret": "12345678"},
            'Your configuration must have a "nameserver" key, '
            'for example: "nameserver: 127.0.0.1"',
        )

    def test_invalid_nameserver_ip(self):
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "lol"},
            'The "nameserver" entry in your configuration is not a valid IP '
            'address: "lol".',
        )

    def test_invalid_dyndns_domain(self):
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "dyndns_domain": "l o l"},
            'The label "l o l" of the hostname "l o l" is invalid.',
        )

    def test_no_zones(self):
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1"},
            'Your configuration must have a "zones" key.',
        )

    def test_zones_string(self):
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "zones": "lol"},
            'Your "zones" key must contain a list of zones.',
        )

    def test_zones_empty_list(self):
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "zones": []},
            "You must have at least one zone configured, for example: "
            '"- name: example.com" and "tsig_key: tPyvZA=="',
        )

    def test_zone_no_name(self):
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "zones": [{"lol": "-"}]},
            'Your zone dictionary must contain a key "name"',
        )

    def test_zone_invalid_zone_name(self):
        config = {
            "secret": "12345678",
            "nameserver": "127.0.0.1",
            "zones": [{"name": "l o l", "tsig_key": "xxx"}],
        }
        self.assert_raises_msg(
            config,
            'The label "l o l" of the hostname "l o l" is invalid.',
        )

    def test_zone_no_tsig_key(self):
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "zones": [{"name": "a"}]},
            'Your zone dictionary must contain a key "tsig_key"',
        )

    def test_zone_invalid_tsig_key(self):
        config = {
            "secret": "12345678",
            "nameserver": "127.0.0.1",
            "zones": [{"name": "a", "tsig_key": "xxx"}],
        }
        self.assert_raises_msg(
            config,
            'Invalid tsig key: "xxx".',
        )

    def test_valid(self):
        config = load_config()
        config = validate_config(config)
        assert config["secret"] == "12345678"
        assert config["dyndns_domain"] == "example.com"


if __name__ == "__main__":
    unittest.main()
