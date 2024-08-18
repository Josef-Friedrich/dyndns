import copy
import os
import re
import unittest
from typing import Any
from unittest import mock

import pytest
from dns.name import EmptyLabel, LabelTooLong, NameTooLong
from pydantic import BaseModel, ValidationError

from dyndns.config import (
    Config,
    IpAddress,
    load_config,
    validate_name,
    validate_secret,
    validate_tsig_key,
)
from dyndns.exceptions import ConfigurationError, DnsNameError
from tests._helper import config_file, files_dir

config: Any = {
    "secret": "12345678",
    "nameserver": "127.0.0.1",
    "zones": [
        {
            "name": "dyndns1.dev.",
            "tsig_key": "aaZI/Ssod3/yqhknm85T3IPKScEU4Q/CbQ2J+QQW9IXeLwkLkxFprkYDoHqre4ECqTfgeu/34DCjHJO8peQc/g==",
        }
    ],
}


def get_config(**kwargs: Any) -> Config:
    config_copy = copy.deepcopy(config)
    config_copy.update(kwargs)
    return Config(**config_copy)


class Ip(BaseModel):
    ip: IpAddress


class TestAnnotatedIpAdress:
    def test_valid(self) -> None:
        ip = Ip(ip="1.2.3.4")
        assert ip.ip == "1.2.3.4"

    def test_invalid(self) -> None:
        with pytest.raises(ValidationError):
            Ip(ip="Invalid")


class TestValidateName:
    def test_dot_is_appended(self) -> None:
        assert validate_name("www.example.com") == "www.example.com."

    def test_numbers(self) -> None:
        assert validate_name("123.123.de") == "123.123.de."

    def test_spaces(self) -> None:
        with pytest.raises(EmptyLabel, match="A DNS label is empty."):
            validate_name("www..com")

    def test_label_to_long(self) -> None:
        with pytest.raises(LabelTooLong, match="A DNS label is > 63 octets long."):
            validate_name(
                "to.looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong.com"
            )

    def test_to_long(self) -> None:
        with pytest.raises(NameTooLong):
            validate_name("abcdefghij." * 24)

    def test_invalid_tld(self) -> None:
        with pytest.raises(
            DnsNameError,
            match="The TLD '777' of the DNS name 'www.example.777' must be not purely numeric.",
        ):
            validate_name("www.example.777")

    def test_invalid_characters(self) -> None:
        with pytest.raises(
            DnsNameError,
            match="The label 'exämple' of the DNS name 'www.exämple.com' is invalid.",
        ):
            validate_name("www.exämple.com")


class TestFunctionValidateTsigKey:
    def assert_raises_msg(self, tsig_key: str, message: str) -> None:
        with pytest.raises(DnsNameError, match=message):
            validate_tsig_key(tsig_key)

    def test_valid(self) -> None:
        assert validate_tsig_key("tPyvZA==") == "tPyvZA=="

    def test_invalid_empty(self) -> None:
        self.assert_raises_msg("", 'Invalid tsig key: "".')

    def test_invalid_string(self) -> None:
        self.assert_raises_msg("xxx", 'Invalid tsig key: "xxx".')


class TestConfig:
    def test_config(self) -> None:
        os.environ["dyndns_CONFIG_FILE"] = config_file
        config = load_config()
        assert config.secret == "12345678"


class TestFunctionValidateSecret:
    def test_valid(self) -> None:
        assert validate_secret("abcd1234") == "abcd1234"

    def test_invalid_to_short(self) -> None:
        with pytest.raises(
            AssertionError,
            match="The secret must be at least 8 characters long. Currently the string is 7 characters long.",
        ):
            validate_secret("1234567")

    def test_invalid_non_alpanumeric(self) -> None:
        with pytest.raises(
            AssertionError,
            match=re.escape(
                "The secret must not contain any non-alphanumeric characters. These characters are permitted: [a-zA-Z0-9]. The following characters are not alphanumeric 'äüö'.",
            ),
        ):
            validate_secret("12345äüö")


class TestPydanticIntegration:
    class TestSecret:
        def test_valid(self) -> None:
            assert get_config(secret="abcd1234").secret == "abcd1234"

        def test_invalid_to_short(self) -> None:
            with pytest.raises(ValidationError):
                get_config(secret="1234567")

        def test_invalid_non_alpanumeric(self) -> None:
            with pytest.raises(ValidationError):
                get_config(secret="12345äüö")

    class TestNameserver:
        def test_ipv4(self) -> None:
            config = get_config(nameserver="1.2.3.4")
            assert str(config.nameserver) == "1.2.3.4"

        def test_ipv6(self) -> None:
            config = get_config(nameserver="1::2")
            assert str(config.nameserver) == "1::2"

        def test_invalid(self) -> None:
            with pytest.raises(ValidationError):
                get_config(nameserver="invalid")

    class TestPort:
        def test_default(self) -> None:
            config = get_config()
            assert config.port == 53

        def test_valid(self) -> None:
            config = get_config(port=42)
            assert config.port == 42

        def test_invalid_less(self) -> None:
            with pytest.raises(ValidationError):
                get_config(port=-1)

        def test_invalid_greater(self) -> None:
            with pytest.raises(ValidationError):
                get_config(port=65536)


class TestFunctionLoadConfig:
    def setup_method(self) -> None:
        os.environ["dyndns_CONFIG_FILE"] = config_file

    def assert_raises_msg(self, config: Config, msg: str) -> None:
        with pytest.raises(ConfigurationError) as e:
            load_config(config)
        assert e.value.args[0] == msg

    @mock.patch("os.path.exists")
    def test_no_config_file(self, exists: mock.Mock) -> None:
        exists.return_value = False
        os.environ["dyndns_CONFIG_FILE"] = "/tmp/dyndns-xxx.yml"
        self.assert_raises_msg(
            None,  # type: ignore
            "The configuration file could not be found.",
        )

    @pytest.mark.skip
    def test_invalid_yaml_format(self) -> None:
        config_file = os.path.join(files_dir, "invalid-yaml.yml")
        os.environ["dyndns_CONFIG_FILE"] = config_file
        self.assert_raises_msg(
            None,  # type: ignore
            "The configuration file is in a invalid YAML format.",
        )

    @pytest.mark.skip
    def test_no_secret(self) -> None:
        self.assert_raises_msg(
            {"test": "test"},  # type: ignore
            'Your configuration must have a "secret" key, for example: '
            '"secret: VDEdxeTKH"',
        )

    @pytest.mark.skip
    def test_invalid_secret(self) -> None:
        self.assert_raises_msg(
            {"secret": "ä"},  # type: ignore
            "The secret must be at least 8 characters long. Currently the string is 1 characters long.",
        )

    @pytest.mark.skip
    def test_no_nameserver(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "port": 53},  # type: ignore
            'Your configuration must have a "nameserver" key, '
            'for example: "nameserver: 127.0.0.1"',
        )

    @pytest.mark.skip
    def test_no_zones(self) -> None:
        self.assert_raises_msg(
            {
                "secret": "12345678",
                "nameserver": "127.0.0.1",
                "port": 53,
            },  # type: ignore
            'Your configuration must have a "zones" key.',
        )

    @pytest.mark.skip
    def test_zones_string(self) -> None:
        self.assert_raises_msg(
            {
                "secret": "12345678",
                "nameserver": "127.0.0.1",
                "port": 53,
                "zones": "test",  # type: ignore
            },
            'Your "zones" key must contain a list of zones.',
        )

    @pytest.mark.skip
    def test_zones_empty_list(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "port": 53, "zones": []},
            "You must have at least one zone configured, for example: "
            '"- name: example.com" and "tsig_key: tPyvZA=="',
        )

    @pytest.mark.skip
    def test_zone_no_name(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "zones": [{"test": "-"}]},  # type: ignore
            'Your zone dictionary must contain a key "name"',
        )

    @pytest.mark.skip
    def test_zone_invalid_zone_name(self) -> None:
        config: Config = {
            "secret": "12345678",
            "nameserver": "127.0.0.1",
            "port": 53,
            "zones": [{"name": "l o l", "tsig_key": "xxx"}],
        }
        self.assert_raises_msg(
            config,
            'The label "l o l" of the hostname "l o l" is invalid.',
        )

    @pytest.mark.skip
    def test_zone_no_tsig_key(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "nameserver": "127.0.0.1", "zones": [{"name": "A"}]},  # type: ignore
            'Your zone dictionary must contain a key "tsig_key"',
        )

    @pytest.mark.skip
    def test_zone_invalid_tsig_key(self) -> None:
        config: Config = {
            "secret": "12345678",
            "nameserver": "127.0.0.1",
            "port": 53,
            "zones": [{"name": "A", "tsig_key": "xxx"}],
        }
        self.assert_raises_msg(
            config,
            'Invalid tsig key: "xxx".',
        )

    def test_valid(self) -> None:
        config: Config = load_config()
        assert config.secret == "12345678"


if __name__ == "__main__":
    unittest.main()
