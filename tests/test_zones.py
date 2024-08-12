import pytest

from dyndns.exceptions import DnsNameError
from dyndns.zones import Zone, ZonesCollection
from tests._helper import zones


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


class TestClassZonesCollection:
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
        assert result is None

    def test_subzones(self) -> None:
        zones = ZonesCollection(
            [
                {"name": "example.com.", "tsig_key": "tPyvZA=="},
                {"name": "dyndns.example.com", "tsig_key": "tPyvZA=="},
            ]
        )
        result = zones.split_fqdn("test.dyndns.example.com")
        assert result == ("test.", "dyndns.example.com.")
