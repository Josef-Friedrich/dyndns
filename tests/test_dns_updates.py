import os
import unittest
from typing import TypedDict
from unittest import mock

import pytest

from dyndns.dns_updates import update_dns_record
from dyndns.exceptions import ParameterError
from tests import _helper


class UpdateDnsRecordKwargs(TypedDict, total=False):
    secret: str
    fqdn: str
    zone_name: str
    record_name: str
    ip_1: str
    ip_2: str


class TestFunctionUpdateDnsRecord:
    def setup_method(self) -> None:
        os.environ["dyndns_CONFIG_FILE"] = _helper.config_file

    def assert_raises_msg(
        self, kwargs: UpdateDnsRecordKwargs, error: type[Exception], msg: str
    ) -> None:
        with pytest.raises(error) as e:
            update_dns_record(**kwargs)
        assert e.value.args[0] == msg

    def test_not_all_three_fqdn_etc(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "fqdn": "a", "zone_name": "b", "record_name": "c"},
            ParameterError,
            'Specify "fqdn" or "zone_name" and "record_name".',
        )

    def test_ip_1_invalid(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "fqdn": "www.example.com", "ip_1": "lol"},
            ParameterError,
            'Invalid ip address "lol"',
        )

    def test_ip_2_invalid(self) -> None:
        self.assert_raises_msg(
            {"secret": "12345678", "fqdn": "www.example.com", "ip_2": "lol"},
            ParameterError,
            'Invalid ip address "lol"',
        )

    def test_both_ip_same_version(self) -> None:
        self.assert_raises_msg(
            {
                "secret": "12345678",
                "fqdn": "www.example.com",
                "ip_1": "1.2.3.4",
                "ip_2": "1.2.3.4",
            },
            ParameterError,
            'The attribute "ipv4" is already set and has the value "1.2.3.4".',
        )

    @mock.patch("dns.query.tcp")
    @mock.patch("dns.update.Update")
    @mock.patch("dns.resolver.Resolver")
    def test_ipv4_update(
        self, Resolver: mock.Mock, Update: mock.Mock, tcp: mock.Mock
    ) -> None:
        resolver = Resolver.return_value
        resolver.resolve.side_effect = [["1.2.3.4"], ["1.2.3.5"]]
        update = Update.return_value
        result = update_dns_record(
            secret="12345678", fqdn="www.example.com", ip_1="1.2.3.5"
        )
        assert (
            result == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: "
            "1.2.3.5\n"
        )
        update.delete.assert_has_calls(
            [
                mock.call("www.example.com.", "a"),
                mock.call("www.example.com.", "aaaa"),
            ]
        )
        update.add.assert_called_with("www.example.com.", 300, "a", "1.2.3.5")


if __name__ == "__main__":
    unittest.main()
