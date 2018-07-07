from dyndns.names import \
    Names, \
    validate_hostname, \
    validate_tsig_key, \
    Zone, \
    Zones
from _helper import zones
from dyndns.exceptions import NamesError
import unittest


class TestFunctionValidateHostname(unittest.TestCase):

    def assertRaisesMsg(self, hostname, msg):
        with self.assertRaises(NamesError) as cm:
            validate_hostname(hostname)
        self.assertEqual(str(cm.exception), msg)

    def test_valid(self):
        self.assertEqual(
            validate_hostname('www.example.com'),
            'www.example.com.',
        )

    def test_invalid_tld(self):
        self.assertRaisesMsg(
            'www.example.777',
            'The TLD "777" of the hostname "www.example.777" must be not '
            'all-numeric.',
        )

    def test_invalid_to_long(self):
        self.assertRaisesMsg(
            'a' * 300,
            'The hostname "aaaaaaaaaa..." is longer than 253 characters.',
        )

    def test_invalid_characters(self):
        self.assertRaisesMsg(
            'www.exämple.com',
            'The label "exämple" of the hostname "www.exämple.com" is '
            'invalid.',
        )


class TestFunctionValidateTsigKey(unittest.TestCase):

    def assertRaisesMsg(self, tsig_key, msg):
        with self.assertRaises(NamesError) as cm:
            validate_tsig_key(tsig_key)
        self.assertEqual(str(cm.exception), msg)

    def test_valid(self):
        self.assertEqual(validate_tsig_key('tPyvZA=='), 'tPyvZA==')

    def test_invalid_empty(self):
        self.assertRaisesMsg('', 'Invalid tsig key: "".')

    def test_invalid_string(self):
        self.assertRaisesMsg('xxx', 'Invalid tsig key: "xxx".')


class TestClassZone(unittest.TestCase):

    def test_init(self):
        zone = Zone('example.com', 'tPyvZA==')
        self.assertEqual(zone.zone_name, 'example.com.')
        self.assertEqual(zone.tsig_key, 'tPyvZA==')

    def test_method_split_fqdn(self):
        zone = Zone('example.com', 'tPyvZA==')
        record_name, zone_name = zone.split_fqdn('www.example.com')
        self.assertEqual(record_name, 'www.')
        self.assertEqual(zone_name, 'example.com.')

    def test_method_build_fqdn(self):
        zone = Zone('example.com', 'tPyvZA==')
        fqdn = zone.build_fqdn('www')
        self.assertEqual(fqdn, 'www.example.com.')


class TestClassZones(unittest.TestCase):

    def test_init(self):
        zone = zones.zones['example.org.']
        self.assertEqual(zone.zone_name, 'example.org.')
        self.assertEqual(zone.tsig_key, 'tPyvZA==')

    def test_method_get_zone_by_name(self):
        zone = zones.get_zone_by_name('example.org')
        self.assertEqual(zone.zone_name, 'example.org.')
        self.assertEqual(zone.tsig_key, 'tPyvZA==')

    def test_method_get_zone_by_name_raises(self):
        with self.assertRaises(NamesError) as cm:
            zones.get_zone_by_name('lol.org')
        self.assertEqual(str(cm.exception), 'Unkown zone "lol.org.".')


class TestClassZonesMethodSplitNames(unittest.TestCase):

    def test_with_dot(self):
        result = zones.split_fqdn('www.example.com')
        self.assertEqual(result, ('www.', 'example.com.'))

    def test_with_org(self):
        result = zones.split_fqdn('www.example.org')
        self.assertEqual(result, ('www.', 'example.org.'))

    def test_unkown_zone(self):
        result = zones.split_fqdn('www.xx.org')
        self.assertEqual(result, False)

    def test_subzones(self):
        zones = Zones([
            {'name': 'example.com.', 'tsig_key': 'tPyvZA=='},
            {'name': 'dyndns.example.com', 'tsig_key': 'tPyvZA=='},
        ])
        result = zones.split_fqdn('lol.dyndns.example.com')
        self.assertEqual(result, ('lol.', 'dyndns.example.com.'))


class TestClassNames(unittest.TestCase):

    def setUp(self):
        self.names = Names(zones=zones, fqdn='www.example.com')

    def test_attribute_fqdn(self):
        self.assertEqual(self.names.fqdn, 'www.example.com.')

    def test_attribute_zone_name(self):
        self.assertEqual(self.names.zone_name, 'example.com.')

    def test_attribute_record_name(self):
        self.assertEqual(self.names.record_name, 'www.')

    def test_attribute_tsig_key(self):
        self.assertEqual(self.names.tsig_key, 'tPyvZA==')


# class TestClassNamesRaises(unittest.TestCase):
#
#     def assertRaisesMsg(self, kwargs, msg):
#         with self.assertRaises(JfErr) as cm:
#             Names(zones, **kwargs)
#         self.assertEqual(str(cm.exception), msg)
#
#     def test_no_kwargs(self):
#         self.assertRaisesMsg({'record_name', 'lol'}, '')


if __name__ == '__main__':
    unittest.main()
