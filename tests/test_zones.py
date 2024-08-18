import pytest

from dyndns.config import ZoneConfig
from dyndns.exceptions import DnsNameError
from dyndns.zones import Zone, ZonesCollection


@pytest.fixture
def zone() -> Zone:
    return Zone("example.com", "tPyvZA==")


class TestClassZone:
    def test_init(self, zone: Zone) -> None:
        assert zone.name == "example.com."
        assert zone.tsig_key == "tPyvZA=="

    class TestMethodGetRecordName:
        def test_specify_fqdn(self, zone: Zone) -> None:
            assert zone.get_record_name("www.example.com") == "www."

        def test_specify_record_name(self, zone: Zone) -> None:
            assert zone.get_record_name("www") == "www."

        def test_specify_foreign_fqdn(self, zone: Zone) -> None:
            assert zone.get_record_name("www.example.org") == "www.example.org."

    class TestMethodGetFqdn:
        def test_specify_record_name(self, zone: Zone) -> None:
            assert zone.get_fqdn("www") == "www.example.com."

        def test_specify_fqdn(self, zone: Zone) -> None:
            assert zone.get_fqdn("www.example.com.") == "www.example.com."

    def test_method_split_fqdn(self, zone: Zone) -> None:
        record_name, zone_name = zone.split_fqdn("www.example.com")
        assert record_name == "www."
        assert zone_name == "example.com."


class TestClassZonesCollection:
    def test_init(self, zones: ZonesCollection) -> None:
        zone = zones.zones["dyndns1.dev."]
        assert zone.name == "dyndns1.dev."
        assert (
            zone.tsig_key
            == "aaZI/Ssod3/yqhknm85T3IPKScEU4Q/CbQ2J+QQW9IXeLwkLkxFprkYDoHqre4ECqTfgeu/34DCjHJO8peQc/g=="
        )

    def test_method_get_zone(self, zones: ZonesCollection) -> None:
        zone = zones.get_zone("dyndns1.dev.")
        assert zone.name == "dyndns1.dev."
        assert (
            zone.tsig_key
            == "aaZI/Ssod3/yqhknm85T3IPKScEU4Q/CbQ2J+QQW9IXeLwkLkxFprkYDoHqre4ECqTfgeu/34DCjHJO8peQc/g=="
        )

    def test_method_get_zone_raises(self, zones: ZonesCollection) -> None:
        with pytest.raises(DnsNameError, match='Unknown zone "test.org".'):
            zones.get_zone("test.org")

    class TestMethodSplitNames:
        def test_zone_name_itself_given_without_dot(
            self, zones: ZonesCollection
        ) -> None:
            result = zones.split_fqdn("dyndns1.dev")
            assert result == ("", "dyndns1.dev.")

        def test_zone_name_itself_given_with_dot(self, zones: ZonesCollection) -> None:
            result = zones.split_fqdn("dyndns1.dev.")
            assert result == ("", "dyndns1.dev.")

        def test_with_dot(self, zones: ZonesCollection) -> None:
            result = zones.split_fqdn("www.dyndns1.dev.")
            assert result == ("www.", "dyndns1.dev.")

        def test_with_second_zone(self, zones: ZonesCollection) -> None:
            result = zones.split_fqdn("www.dyndns2.dev.")
            assert result == ("www.", "dyndns2.dev.")

        def test_unkown_zone(self, zones: ZonesCollection) -> None:
            result = zones.split_fqdn("www.xx.org")
            assert result is None

        def test_subzones(self) -> None:
            zones = ZonesCollection(
                [
                    ZoneConfig(**{"name": "example.com.", "tsig_key": "tPyvZA=="}),
                    ZoneConfig(
                        **{"name": "dyndns.example.com", "tsig_key": "tPyvZA=="}
                    ),
                ]
            )
            result = zones.split_fqdn("test.dyndns.example.com")
            assert result == ("test.", "dyndns.example.com.")
