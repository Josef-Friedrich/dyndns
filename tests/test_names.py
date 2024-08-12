import pytest

from dyndns.dns_ng import validate_tsig_key
from dyndns.exceptions import DnsNameError
from dyndns.names import (
    FullyQualifiedDomainName,
    validate_dns_name,
)
from dyndns.zones import Zone, ZonesCollection
from tests._helper import zones


class TestFunctionValidateHostname:
    def assert_raises_msg(self, hostname: str, msg: str) -> None:
        with pytest.raises(DnsNameError, match=msg):
            validate_dns_name(hostname)

    def test_valid(self) -> None:
        assert validate_dns_name("www.example.com") == "www.example.com."

    def test_invalid_tld(self) -> None:
        self.assert_raises_msg(
            "www.example.777",
            'The TLD "777" of the DNS name "www.example.777" must be not all-numeric.',
        )

    def test_invalid_to_long(self) -> None:
        self.assert_raises_msg(
            "a" * 300,
            'The DNS name "aaaaaaaaaa..." is longer than 253 characters.',
        )

    def test_invalid_characters(self) -> None:
        self.assert_raises_msg(
            "www.exämple.com",
            'The label "exämple" of the hostname "www.exämple.com" is invalid.',
        )


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


class TestClassZone:
    def test_init(self) -> None:
        zone = Zone("example.com", "tPyvZA==")
        assert zone.name == "example.com."
        assert zone.tsig_key == "tPyvZA=="

    def test_method_split_fqdn(self) -> None:
        zone = Zone("example.com", "tPyvZA==")
        record_name, zone_name = zone.split_fqdn("www.example.com")
        assert record_name == "www."
        assert zone_name == "example.com."

    def test_method_build_fqdn(self) -> None:
        zone = Zone("example.com", "tPyvZA==")
        fqdn = zone.build_fqdn("www")
        assert fqdn == "www.example.com."


class TestClassZones:
    def test_init(self) -> None:
        zone = zones.zones["example.org."]
        assert zone.name == "example.org."
        assert zone.tsig_key == "tPyvZA=="

    def test_method_get_zone_by_name(self) -> None:
        zone = zones.get_zone_by_name("example.org")
        assert zone.name == "example.org."
        assert zone.tsig_key == "tPyvZA=="

    def test_method_get_zone_by_name_raises(self) -> None:
        with pytest.raises(DnsNameError, match='Unkown zone "test.org.".'):
            zones.get_zone_by_name("test.org")


class TestClassZonesMethodSplitNames:
    def test_with_dot(self) -> None:
        result = zones.split_fqdn("www.example.com")
        assert result == ("www.", "example.com.")

    def test_with_org(self) -> None:
        result = zones.split_fqdn("www.example.org")
        assert result == ("www.", "example.org.")

    def test_unkown_zone(self) -> None:
        result = zones.split_fqdn("www.xx.org")
        assert result is False

    def test_subzones(self) -> None:
        zones = ZonesCollection(
            [
                {"name": "example.com.", "tsig_key": "tPyvZA=="},
                {"name": "dyndns.example.com", "tsig_key": "tPyvZA=="},
            ]
        )
        result = zones.split_fqdn("test.dyndns.example.com")
        assert result == ("test.", "dyndns.example.com.")


class TestClassNames:
    fqdn: FullyQualifiedDomainName

    def setup_method(self) -> None:
        self.fqdn = FullyQualifiedDomainName(zones=zones, fqdn="www.example.com")

    def test_attribute_fqdn(self) -> None:
        assert self.fqdn.fqdn == "www.example.com."

    def test_attribute_zone_name(self) -> None:
        assert self.fqdn.zone_name == "example.com."

    def test_attribute_record_name(self) -> None:
        assert self.fqdn.record_name == "www."

    def test_attribute_tsig_key(self) -> None:
        assert self.fqdn.tsig_key == "tPyvZA=="
