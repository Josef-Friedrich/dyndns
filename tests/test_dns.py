import copy
import ipaddress
from unittest import mock

import pytest

from dyndns.dns import DnsUpdate
from dyndns.ipaddresses import IpAddressContainer
from dyndns.names import FullyQualifiedDomainName
from dyndns.types import LogLevel
from tests import _helper

ipaddresses = IpAddressContainer(ipv4="1.2.3.4")
zones = _helper.zones
names = FullyQualifiedDomainName(zones, fqdn="www.example.com")

NO_INTERNET_CONNECTIFITY = not _helper.check_internet_connectifity()


class TestClassDnsUpdate:
    def test_method_build_tsigkeyring(self) -> None:
        dns_update = DnsUpdate("127.0.0.1", names, ipaddresses)
        result = dns_update._build_tsigkeyring(  # type: ignore
            dns_update.fqdn.zone_name, dns_update.fqdn.tsig_key
        )
        for zone, tsig_key in result.items():
            assert str(zone) == "example.com."
            assert tsig_key == b"\xb4\xfc\xafd"

    def test_method_convert_record_type(self) -> None:
        assert DnsUpdate._convert_record_type(4) == "a"  # type: ignore
        assert DnsUpdate._convert_record_type(6) == "aaaa"  # type: ignore

    @pytest.mark.skipif(NO_INTERNET_CONNECTIFITY, reason="No uplink")
    def test_method_resolve_unpatched(self) -> None:
        _names = copy.deepcopy(names)
        _names.zone_name = "google.com."
        dns = DnsUpdate("8.8.8.8", _names, ipaddresses)
        ip = dns._resolve(4)  # type: ignore
        ipaddress.ip_address(ip)

    @mock.patch("dns.resolver.Resolver")
    def test_method_resolve_patched(self, Resolver: mock.Mock) -> None:
        resolver = Resolver.return_value
        resolver.resolve.return_value = ["1.2.3.4"]
        dns_update = DnsUpdate("8.8.8.8", names, ipaddresses)
        ip = dns_update._resolve(4)  # type: ignore
        ipaddress.ip_address(ip)
        assert ip == "1.2.3.4"

    @mock.patch("dns.query.tcp")
    @mock.patch("dns.update.Update")
    @mock.patch("dns.resolver.Resolver")
    def test_method_set_record_updated(
        self, Resolver: mock.Mock, Update: mock.Mock, tcp: mock.Mock
    ) -> None:
        resolver = Resolver.return_value
        resolver.resolve.side_effect = [["1.2.3.4"], ["1.2.3.5"]]
        update = Update.return_value

        dns = DnsUpdate("127.0.0.1", names, ipaddresses)
        result = dns._set_record("1.2.3.5", 4)  # type: ignore

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
            "status": LogLevel.UPDATED,
        }

    @mock.patch("dns.query.tcp")
    @mock.patch("dns.update.Update")
    @mock.patch("dns.resolver.Resolver")
    def test_method_set_record_unchanged(
        self, Resolver: mock.Mock, Update: mock.Mock, tcp: mock.Mock
    ) -> None:
        resolver = Resolver.return_value
        resolver.resolve.return_value = ["1.2.3.4"]
        update = Update.return_value

        dns_update = DnsUpdate("127.0.0.1", names, ipaddresses)
        result = dns_update._set_record("1.2.3.4", 4)  # type: ignore

        update.delete.assert_not_called()
        update.add.assert_not_called()

        assert result == {
            "ip_version": 4,
            "new_ip": "1.2.3.4",
            "old_ip": "1.2.3.4",
            "status": LogLevel.UNCHANGED,
        }

    @mock.patch("dns.query.tcp")
    @mock.patch("dns.update.Update")
    @mock.patch("dns.resolver.Resolver")
    def test_method_set_record_error(
        self, Resolver: mock.Mock, Update: mock.Mock, tcp: mock.Mock
    ) -> None:
        resolver = Resolver.return_value
        resolver.resolve.return_value = ["1.2.3.4"]

        dns_update = DnsUpdate("127.0.0.1", names, ipaddresses)
        result = dns_update._set_record("1.2.3.5", 4)  # type: ignore

        assert result == {
            "ip_version": 4,
            "new_ip": "1.2.3.5",
            "old_ip": "1.2.3.4",
            "status": LogLevel.DNS_SERVER_ERROR,
        }
