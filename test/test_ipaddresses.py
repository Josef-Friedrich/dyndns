from jfddns.ipaddresses import IpAddresses
from jfddns.validate import JfErr
import unittest


class TestClassIpAddresses(unittest.TestCase):

    def assertRaisesMsg(self, kwargs, msg):
        with self.assertRaises(JfErr) as cm:
            IpAddresses(**kwargs)

        self.assertEqual(str(cm.exception), msg)

    def test_invalid_ipv4(self):
        self.assertRaisesMsg({'ipv4': 'lol'}, 'Invalid ip address "lol"')

    def test_invalid_ipv4_version(self):
        self.assertRaisesMsg(
            {'ipv4': '1::2'},
            'IP version "4" does not match.'
        )

    def test_no_ip(self):
        self.assertRaisesMsg({}, 'No ip address set.')


if __name__ == '__main__':
    unittest.main()
