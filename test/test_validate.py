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


if __name__ == '__main__':
    unittest.main()
