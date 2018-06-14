import unittest
from jfddns import log


class TestMethodMsg(unittest.TestCase):

    def test_msg(self):
        self.assertEqual(log.msg('lol', 'UNCHANGED'), 'UNCHANGED: lol')


if __name__ == '__main__':
    unittest.main()
