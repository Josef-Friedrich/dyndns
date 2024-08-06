import unittest

import pytest
from _helper import zones

from dyndns.exceptions import NamesError
from dyndns.names import Names, Zone, Zones, validate_hostname, validate_tsig_key


class TestFunctionValidateHostname:
    def assert_raises_msg(self, hostname, msg):
        with pytest.raises(NamesError) as e:
            validate_hostname(hostname)
        assert e.value.args[0] == msg

    def test_valid(self):
        assert validate_hostname("www.example.com") == "www.example.com."

    def test_invalid_tld(self):
        self.assert_raises_msg(
            "www.example.777",
            'The TLD "777" of the hostname "www.example.777" must be not '
            "all-numeric.",
        )

    def test_invalid_to_long(self):
        self.assert_raises_msg(
            "a" * 300,
            'The hostname "aaaaaaaaaa..." is longer than 253 characters.',
        )

    def test_invalid_characters(self):
        self.assert_raises_msg(
            "www.exämple.com",
            'The label "exämple" of the hostname "www.exämple.com" is ' "invalid.",
        )


class TestFunctionValidateTsigKey:
    def assert_raises_msg(self, tsig_key, msg):
        with pytest.raises(NamesError) as e:
            validate_tsig_key(tsig_key)
        assert e.value.args[0] == msg

    def test_valid(self):
        assert validate_tsig_key("tPyvZA==") == "tPyvZA=="

    def test_invalid_empty(self):
        self.assert_raises_msg("", 'Invalid tsig key: "".')

    def test_invalid_string(self):
        self.assert_raises_msg("xxx", 'Invalid tsig key: "xxx".')


class TestClassZone:
    def test_init(self):
        zone = Zone("example.com", "tPyvZA==")
        assert zone.zone_name == "example.com."
        assert zone.tsig_key == "tPyvZA=="

    def test_method_split_fqdn(self):
        zone = Zone("example.com", "tPyvZA==")
        record_name, zone_name = zone.split_fqdn("www.example.com")
        assert record_name == "www."
        assert zone_name == "example.com."

    def test_method_build_fqdn(self):
        zone = Zone("example.com", "tPyvZA==")
        fqdn = zone.build_fqdn("www")
        assert fqdn == "www.example.com."


class TestClassZones:
    def test_init(self):
        zone = zones.zones["example.org."]
        assert zone.zone_name == "example.org."
        assert zone.tsig_key == "tPyvZA=="

    def test_method_get_zone_by_name(self):
        zone = zones.get_zone_by_name("example.org")
        assert zone.zone_name == "example.org."
        assert zone.tsig_key == "tPyvZA=="

    def test_method_get_zone_by_name_raises(self):
        with pytest.raises(NamesError, match='Unkown zone "lol.org.".'):
            zones.get_zone_by_name("lol.org")


class TestClassZonesMethodSplitNames:
    def test_with_dot(self):
        result = zones.split_fqdn("www.example.com")
        assert result == ("www.", "example.com.")

    def test_with_org(self):
        result = zones.split_fqdn("www.example.org")
        assert result == ("www.", "example.org.")

    def test_unkown_zone(self):
        result = zones.split_fqdn("www.xx.org")
        assert result == False

    def test_subzones(self):
        zones = Zones(
            [
                {"name": "example.com.", "tsig_key": "tPyvZA=="},
                {"name": "dyndns.example.com", "tsig_key": "tPyvZA=="},
            ]
        )
        result = zones.split_fqdn("lol.dyndns.example.com")
        assert result == ("lol.", "dyndns.example.com.")


class TestClassNames:
    def setup_method(self):
        self.names = Names(zones=zones, fqdn="www.example.com")

    def test_attribute_fqdn(self):
        assert self.names.fqdn == "www.example.com."

    def test_attribute_zone_name(self):
        assert self.names.zone_name == "example.com."

    def test_attribute_record_name(self):
        assert self.names.record_name == "www."

    def test_attribute_tsig_key(self):
        assert self.names.tsig_key == "tPyvZA=="


# class TestClassNamesRaises(unittest.TestCase):
#
#     def assertRaisesMsg(self, kwargs, msg):
#         with self.assertRaises(JfErr) as cm:
#             Names(zones, **kwargs)
#         self.assertEqual(str(cm.exception), msg)
#
#     def test_no_kwargs(self):
#         self.assertRaisesMsg({'record_name', 'lol'}, '')


if __name__ == "__main__":
    unittest.main()
