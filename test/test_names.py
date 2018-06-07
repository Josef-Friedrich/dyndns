from jfddns.names import \
    Fqdn, \
    validate_hostname, \
    validate_tsig_key, \
    Zone, \
    Zones
from jfddns.validate import JfErr
import unittest

zones = Zones([
    {'name': 'example.com.', 'tsig_key': 'tPyvZA=='},
    {'name': 'example.org', 'tsig_key': 'tPyvZA=='},
])


class TestFunctionValidateHostname(unittest.TestCase):

    def assertRaisesMsg(self, hostname, msg):
        with self.assertRaises(JfErr) as cm:
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
        with self.assertRaises(JfErr) as cm:
            validate_tsig_key(tsig_key)
        print(str(cm.exception))
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


class TestClassZonesMethodSplitFqdn(unittest.TestCase):

    def test_with_dot(self):
        result = zones.split_fqdn('www.example.com')
        self.assertEqual(result, ('www.', 'example.com.'))

    def test_with_org(self):
        result = zones.split_fqdn('www.example.org')
        self.assertEqual(result, ('www.', 'example.org.'))

    def test_unkown_zone(self):
        result = zones.split_fqdn('www.xx.org')
        self.assertEqual(result, False)


class TestClassFqdn(unittest.TestCase):

    def test_init(self):
        fqdn = Fqdn(zones=zones, fqdn='www.example.com')
        self.assertEqual(fqdn.fqdn, 'www.example.com.')
        self.assertEqual(fqdn.zone_name, 'example.com.')
        self.assertEqual(fqdn.record_name, 'www.')


if __name__ == '__main__':
    unittest.main()
