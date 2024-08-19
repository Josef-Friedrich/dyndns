import copy
import os
import re
from typing import Any
from unittest import mock

import pytest
import yaml
import yaml.scanner
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
from dyndns.exceptions import DnsNameError
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
    for key, value in kwargs.items():
        if value is None:
            del config_copy[key]
        else:
            config_copy[key] = value
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


class TestFunctionLoadConfig:
    def test_load_from_enviroment_valiable(self) -> None:
        os.environ["dyndns_CONFIG_FILE"] = config_file
        config: Config = load_config()
        assert config.secret == "12345678"

    @mock.patch("os.path.exists")
    def test_no_config_file(self, exists: mock.Mock) -> None:
        exists.return_value = False
        with pytest.raises(FileNotFoundError):
            load_config("/tmp/dyndns-xxx.yml")

    def test_invalid_yaml_format(self) -> None:
        with pytest.raises(yaml.scanner.ScannerError):
            load_config(os.path.join(files_dir, "invalid-yaml.yml"))


class TestConfig:
    def test_valid(self) -> None:
        config: Config = get_config()
        assert config.secret == "12345678"
        assert str(config.nameserver) == "127.0.0.1"
        assert config.port == 53
        assert config.zones[0].name == "dyndns1.dev."
        assert (
            config.zones[0].tsig_key
            == "aaZI/Ssod3/yqhknm85T3IPKScEU4Q/CbQ2J+QQW9IXeLwkLkxFprkYDoHqre4ECqTfgeu/34DCjHJO8peQc/g=="
        )

    class TestSecret:
        def test_valid(self) -> None:
            assert get_config(secret="abcd1234").secret == "abcd1234"

        def test_invalid_to_short(self) -> None:
            with pytest.raises(ValidationError):
                get_config(secret="1234567")

        def test_invalid_non_alpanumeric(self) -> None:
            with pytest.raises(ValidationError):
                get_config(secret="12345äüö")

        def test_none(self) -> None:
            with pytest.raises(ValidationError):
                get_config(secret=None)

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

        def test_none(self) -> None:
            with pytest.raises(ValidationError):
                get_config(nameserver=None)

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

    class TestZones:
        def test_none(self) -> None:
            with pytest.raises(ValidationError):
                get_config(zones=None)

        def test_string(self) -> None:
            with pytest.raises(ValidationError):
                get_config(zones="zones")

        def test_empty_list(self) -> None:
            with pytest.raises(ValidationError):
                get_config(zones=[])

        def test_no_name(self) -> None:
            with pytest.raises(ValidationError):
                get_config(zones=[{"no_name": "-"}])

        def test_invalid_zone_name(self) -> None:
            with pytest.raises(DnsNameError):
                get_config(
                    zones=[
                        {
                            "name": "in valid.dev.",
                            "tsig_key": "aaZI/Ssod3/yqhknm85T3IPKScEU4Q/CbQ2J+QQW9IXeLwkLkxFprkYDoHqre4ECqTfgeu/34DCjHJO8peQc/g==",
                        }
                    ]
                )

        def test_no_tsig_key(self) -> None:
            with pytest.raises(ValidationError):
                get_config(zones=[{"name": "dyndns1.dev."}])

        def test_invalid_tsig_key(self) -> None:
            with pytest.raises(DnsNameError):
                get_config(zones=[{"name": "dyndns1.dev.", "tsig_key": "xxx"}])
