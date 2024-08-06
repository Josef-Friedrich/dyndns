import copy
import ipaddress
import unittest
from unittest import mock

import _helper
import pytest

from dyndns.dns import DnsUpdate
from dyndns.ipaddresses import IpAddressContainer
from dyndns.names import Names

ipaddresses = IpAddressContainer(ipv4="1.2.3.4")
zones = _helper.zones
names = Names(zones, fqdn="www.example.com")

NO_INTERNET_CONNECTIFITY = not _helper.check_internet_connectifity()


class TestClassDnsUpdate:
    def test_method_build_tsigkeyring(self):
        du = DnsUpdate("127.0.0.1", names, ipaddresses)
        result = du._build_tsigkeyring(du.names.zone_name, du.names.tsig_key)
        for zone, tsig_key in result.items():
            assert str(zone) == "example.com."
            assert tsig_key == b"\xb4\xfc\xafd"

    def test_method_convert_record_type(self):
        assert DnsUpdate._convert_record_type(4) == "a"
        assert DnsUpdate._convert_record_type(6) == "aaaa"

    @pytest.mark.skipif(NO_INTERNET_CONNECTIFITY, reason="No uplink")
    def test_method_resolve_unpatched(self):
        _names = copy.deepcopy(names)
        _names.zone_name = "google.com."
        dns = DnsUpdate("8.8.8.8", _names, ipaddresses)
        ip = dns._resolve(4)
        ipaddress.ip_address(ip)

    @mock.patch("dns.resolver.Resolver")
    def test_method_resolve_patched(self, Resolver):
        resolver = Resolver.return_value
        resolver.query.return_value = ["1.2.3.4"]
        dns = DnsUpdate("8.8.8.8", names, ipaddresses)
        ip = dns._resolve(4)
        ipaddress.ip_address(ip)
        assert ip == "1.2.3.4"

    @mock.patch("dns.query.tcp")
    @mock.patch("dns.update.Update")
    @mock.patch("dns.resolver.Resolver")
    def test_method_set_record_updated(self, Resolver, Update, tcp):
        resolver = Resolver.return_value
        resolver.query.side_effect = [["1.2.3.4"], ["1.2.3.5"]]
        update = Update.return_value

        dns = DnsUpdate("127.0.0.1", names, ipaddresses)
        dns.record_name = "www"
        result = dns._set_record("1.2.3.5", 4)

        update.delete.assert_has_calls(
            [
                mock.call("www.example.com.", "a"),
                mock.call("www.example.com.", "aaaa"),
            ]
        )
        update.add.assert_called_with("www.example.com.", 300, "a", "1.2.3.5")
        assert tcp.call_args[1]["where"] == "127.0.0.1"
        Update.assert_called()

        assert result == {
            "ip_version": 4,
            "new_ip": "1.2.3.5",
            "old_ip": "1.2.3.4",
            "status": "UPDATED",
        }

    @mock.patch("dns.query.tcp")
    @mock.patch("dns.update.Update")
    @mock.patch("dns.resolver.Resolver")
    def test_method_set_record_unchanged(self, Resolver, Update, tcp):
        resolver = Resolver.return_value
        resolver.query.return_value = ["1.2.3.4"]
        update = Update.return_value

        dns = DnsUpdate("127.0.0.1", names, ipaddresses)
        dns.record_name = "www"
        result = dns._set_record("1.2.3.4", 4)

        update.delete.assert_not_called()
        update.add.assert_not_called()

        assert result == {
            "ip_version": 4,
            "new_ip": "1.2.3.4",
            "old_ip": "1.2.3.4",
            "status": "UNCHANGED",
        }

    @mock.patch("dns.query.tcp")
    @mock.patch("dns.update.Update")
    @mock.patch("dns.resolver.Resolver")
    def test_method_set_record_error(self, Resolver, Update, tcp):
        resolver = Resolver.return_value
        resolver.query.return_value = ["1.2.3.4"]

        dns = DnsUpdate("127.0.0.1", names, ipaddresses)
        dns.record_name = "www"
        result = dns._set_record("1.2.3.5", 4)

        assert result == {
            "ip_version": 4,
            "new_ip": "1.2.3.5",
            "old_ip": "1.2.3.4",
            "status": "DNS_SERVER_ERROR",
        }
