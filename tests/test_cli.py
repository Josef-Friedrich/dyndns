import subprocess
import unittest


class TestCli(unittest.TestCase):

    def test_help(self):
        out = subprocess.run(['dyndns-debug', '--help'], encoding='utf-8',
                             stdout=subprocess.PIPE)
        self.assertEqual(out.returncode, 0)
        self.assertTrue(out.stdout)

    def test_version(self):
        out = subprocess.run(['dyndns-debug', '--version'], encoding='utf-8',
                             stdout=subprocess.PIPE)
        self.assertEqual(out.returncode, 0)
        self.assertTrue(out.stdout)
