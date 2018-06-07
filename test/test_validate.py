from jfddns import validate
from jfddns.validate import JfErr
import unittest


class TestMethodSecret(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(validate.secret('abcd1234'), 'abcd1234')

    def test_invalid_to_short(self):
        with self.assertRaises(JfErr):
            validate.secret('1234567')

    def test_invalid_non_alpanumeric(self):
        with self.assertRaises(JfErr):
            validate.secret('12345äüö')


class TestMethodIpv4(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(validate.ipv4('192.168.2.3'), '192.168.2.3')

    def test_invalid_string(self):
        self.assertFalse(validate.ipv4('lol'))

    def test_invalid_ipv6(self):
        self.assertFalse(validate.ipv4('1::2'))


class TestMethodIpv6(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(validate.ipv6('1::2'), '1::2')

    def test_invalid_string(self):
        self.assertFalse(validate.ipv6('lol'))

    def test_invalid_ipv6(self):
        self.assertFalse(validate.ipv6('1.2.3.4'))


class TestMethodIp(unittest.TestCase):

    def test_ipv4(self):
        self.assertEqual(validate.ip('1.2.3.4'), ('1.2.3.4', 4))

    def test_ipv6(self):
        self.assertEqual(validate.ip('1::2'), ('1::2', 6))

    def test_invalid(self):
        self.assertFalse(validate.ip('lol'))


class TestMethodTsigKey(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(validate.tsig_key('tPyvZA=='), 'tPyvZA==')

    def test_invalid_empty(self):
        self.assertEqual(validate.tsig_key(''), False)

    def test_invalid_list(self):
        self.assertEqual(validate.tsig_key('xxx'), False)


class TestMethodZone(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(validate.zone('github.com'), 'github.com')


class TestMethodRecord(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(validate.record('sub'), 'sub')


if __name__ == '__main__':
    unittest.main()
