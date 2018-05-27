import unittest
from jfddns import load_config
import os


class TestConfig(unittest.TestCase):

    def test_config(self):
        config = load_config(os.path.join(os.path.dirname(__file__), 'config.yml'))
        self.assertEqual(config['secret'], 12345)


if __name__ == '__main__':
    unittest.main()
