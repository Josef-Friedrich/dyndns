import unittest
from jfddns import load_config, Validate
import os


class TestConfig(unittest.TestCase):

    def test_config(self):
        config = load_config(os.path.join(os.path.dirname(__file__),
                             'config.yml'))
        self.assertEqual(config['secret'], 12345)


class TestValidate(unittest.TestCase):

    def test_ipv4_valid(self):
        self.assertEqual(str(Validate.ipv4('192.168.2.3')), '192.168.2.3')

    def test_ipv4_invalid_string(self):
        with self.assertRaises(ValueError):
            Validate.ipv4('lol')

    def test_ipv4_invalid_ipv6(self):
        with self.assertRaises(ValueError):
            Validate.ipv4('1::2')

    def test_ipv6_valid(self):
        self.assertEqual(str(Validate.ipv6('1::2')), '1::2')

    def test_ipv6_invalid_string(self):
        with self.assertRaises(ValueError):
            Validate.ipv6('lol')

    def test_ipv6_invalid_ipv6(self):
        with self.assertRaises(ValueError):
            Validate.ipv6('1.2.3.4')

    def test_zone_valid(self):
        self.assertEqual(str(Validate.zone('github.com')), 'github.com.')

    def test_record_valid(self):
        self.assertEqual(str(Validate.record('sub')), 'sub.')


if __name__ == '__main__':
    unittest.main()
