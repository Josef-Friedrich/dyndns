from jfddns.names import validate_hostname
from jfddns.validate import JfErr
import unittest


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


if __name__ == '__main__':
    unittest.main()
