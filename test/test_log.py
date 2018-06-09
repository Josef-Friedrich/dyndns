import unittest
from jfddns import log


class TestMethodMsg(unittest.TestCase):

    def test_msg(self):
        log.msg('lol')


if __name__ == '__main__':
    unittest.main()
