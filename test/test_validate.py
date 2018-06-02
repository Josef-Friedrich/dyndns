from jfddns import validate
import unittest


class TestMethodSecret(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(validate.secret('abcd1234'), 'abcd1234')

    def test_invalid_to_short(self):
        self.assertEqual(validate.secret('1234567'), False)

    def test_invalid_non_alpanumeric(self):
        self.assertEqual(validate.secret('12345äüö'), False)


class TestMethodIpv4(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(str(validate.ipv4('192.168.2.3')), '192.168.2.3')

    def test_invalid_string(self):
        self.assertFalse(validate.ipv4('lol'))

    def test_invalid_ipv6(self):
        self.assertFalse(validate.ipv4('1::2'))


class TestMethodIpv6(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(str(validate.ipv6('1::2')), '1::2')

    def test_invalid_string(self):
        self.assertFalse(validate.ipv6('lol'))

    def test_invalid_ipv6(self):
        self.assertFalse(validate.ipv6('1.2.3.4'))


class TestMethodZone(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(validate.zone('github.com'), 'github.com')


class TestMethodRecord(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(validate.record('sub'), 'sub')


if __name__ == '__main__':
    unittest.main()
