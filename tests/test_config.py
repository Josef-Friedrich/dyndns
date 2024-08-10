import os
import unittest
from unittest import mock

import pytest

from dyndns.config import load_config, validate_config, validate_secret
from dyndns.exceptions import ConfigurationError
from dyndns.types import Config
from tests._helper import config_file, files_dir


class TestConfig:
    def test_config(self) -> None:
        os.environ["dyndns_CONFIG_FILE"] = config_file
        config = load_config()
        assert config["secret"] == 12345678


class TestFunctionValidateSecret:
    def test_valid(self) -> None:
        assert validate_secret("abcd1234") == "abcd1234"

    def test_invalid_to_short(self) -> None:
        with pytest.raises(ConfigurationError):
            validate_secret("1234567")

    def test_invalid_non_alpanumeric(self) -> None:
        with pytest.raises(ConfigurationError):
            validate_secret("12345äüö")


class TestFunctionValidateConfig:
    def setup_method(self) -> None:
        os.environ["dyndns_CONFIG_FILE"] = config_file

    def assert_raises_msg(self, config: Config, msg: str) -> None:
        with pytest.raises(ConfigurationError) as e:
            validate_config(config)
        assert e.value.args[0] == msg

    @mock.patch("os.path.exists")
    def test_no_config_file(self, exists: mock.Mock) -> None:
        exists.return_value = False
        os.environ["dyndns_CONFIG_FILE"] = "/tmp/dyndns-xxx.yml"
        self.assert_raises_msg(
            None,  # type: ignore
            "The configuration file could not be found.",
        )

    def test_invalid_yaml_format(self) -> None:
        config_file = os.path.join(files_dir, "invalid-yaml.yml")
        os.environ["dyndns_CONFIG_FILE"] = config_file
        self.assert_raises_msg(
            None,  # type: ignore
            "The configuration file is in a invalid YAML format.",
        )

    def test_no_secret(self) -> None:
        self.assert_raises_msg(
            {"test": "test"},  # type: ignore
            'Your configuration must have a "secret" key, for example: '
            '"secret: VDEdxeTKH"',
        )

    def test_invalid_secret(self) -> None:
        self.assert_raises_msg(
            {"secret": "ä"},  # type: ignore
            "The secret must be at least 8 characters long and may not "
            "contain any non-alpha-numeric characters.",
        )

    def test_no_nameserver(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678"},  # type: ignore
            'Your configuration must have a "nameserver" key, '
            'for example: "nameserver: 127.0.0.1"',
        )

    def test_invalid_nameserver_ip(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "test"},  # type: ignore
            'The "nameserver" entry in your configuration is not a valid IP '
            'address: "test".',
        )

    def test_invalid_dyndns_domain(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "dyndns_domain": "l o l"},  # type: ignore
            'The label "l o l" of the hostname "l o l" is invalid.',
        )

    def test_no_zones(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1"},  # type: ignore
            'Your configuration must have a "zones" key.',
        )

    def test_zones_string(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "zones": "test"},  # type: ignore
            'Your "zones" key must contain a list of zones.',
        )

    def test_zones_empty_list(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "zones": []},
            "You must have at least one zone configured, for example: "
            '"- name: example.com" and "tsig_key: tPyvZA=="',
        )

    def test_zone_no_name(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "zones": [{"test": "-"}]},  # type: ignore
            'Your zone dictionary must contain a key "name"',
        )

    def test_zone_invalid_zone_name(self) -> None:
        config: Config = {
            "secret": "12345678",
            "nameserver": "127.0.0.1",
            "zones": [{"name": "l o l", "tsig_key": "xxx"}],
        }
        self.assert_raises_msg(
            config,
            'The label "l o l" of the hostname "l o l" is invalid.',
        )

    def test_zone_no_tsig_key(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "zones": [{"name": "a"}]},  # type: ignore
            'Your zone dictionary must contain a key "tsig_key"',
        )

    def test_zone_invalid_tsig_key(self) -> None:
        config: Config = {
            "secret": "12345678",
            "nameserver": "127.0.0.1",
            "zones": [{"name": "a", "tsig_key": "xxx"}],
        }
        self.assert_raises_msg(
            config,
            'Invalid tsig key: "xxx".',
        )

    def test_valid(self) -> None:
        config: Config = load_config()
        config = validate_config(config)
        assert config["secret"] == "12345678"
        assert "dyndns_domain" in config
        assert config["dyndns_domain"] == "example.com"


if __name__ == "__main__":
    unittest.main()
