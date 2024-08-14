import pytest

from dyndns.exceptions import DnsNameError
from dyndns.zones import Zone, ZonesCollection
from tests._helper import zones


class TestClassZone:
    zone: Zone

    def setup_method(self) -> None:
        self.zone = Zone("example.com", "tPyvZA==")

    def test_init(self) -> None:
        assert self.zone.name == "example.com."
        assert self.zone.tsig_key == "tPyvZA=="

    def test_method_get_record_name(self) -> None:
        assert self.zone.get_record_name("www.example.com") == "www."

    def test_method_get_record_name_record_name_given(self) -> None:
        assert self.zone.get_record_name("www") == "www."

    def test_method_get_record_name_foreign_fqdn_given(self) -> None:
        assert self.zone.get_record_name("www.example.org") == "www.example.org."

    def test_method_split_fqdn(self) -> None:
        record_name, zone_name = self.zone.split_fqdn("www.example.com")
        assert record_name == "www."
        assert zone_name == "example.com."

    def test_method_build_fqdn(self) -> None:
        assert self.zone.build_fqdn("www") == "www.example.com."

    def test_method_build_fqdn_specified_as_fqdn(self) -> None:
        assert self.zone.build_fqdn("www.example.com.") == "www.example.com."


class TestClassZonesCollection:
    def test_init(self) -> None:
        zone = zones.zones["example.org."]
        assert zone.name == "example.org."
        assert zone.tsig_key == "tPyvZA=="

    def test_method_get_zone(self) -> None:
        zone = zones.get_zone("example.org")
        assert zone.name == "example.org."
        assert zone.tsig_key == "tPyvZA=="

    def test_method_get_zone_raises(self) -> None:
        with pytest.raises(DnsNameError, match='Unknown zone "test.org".'):
            zones.get_zone("test.org")

    class TestMethodSplitNames:
        def test_zone_name_itself_given_without_dot(self) -> None:
            result = zones.split_fqdn("example.com")
            assert result == ("", "example.com.")

        def test_zone_name_itself_given_with_dot(self) -> None:
            result = zones.split_fqdn("example.com.")
            assert result == ("", "example.com.")

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
