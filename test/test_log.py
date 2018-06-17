from jfddns import log
from jfddns.log import UpdatesDB
import os
import unittest


def clean_log_file(log_file_path):
    log_file = open(log_file_path, 'w')
    log_file.write('')
    log_file.close()


class TestMethodMsg(unittest.TestCase):

    def setUp(self):
        self.log_file = log.log_file
        clean_log_file(self.log_file)

    def test_msg(self):
        self.assertEqual(log.msg('lol', 'UNCHANGED'), 'UNCHANGED: lol')

    def test_log_file(self):
        log.msg('lol', 'UNCHANGED')
        log_file = open(log.log_file, 'r')
        result = log_file.read()
        self.assertIn('UNCHANGED', result)
        self.assertIn('lol', result)


class TestClassUpdateDB(unittest.TestCase):

    def test_init(self):
        db = UpdatesDB()
        self.assertEqual(db.db_file, os.path.join(os.getcwd(), 'jfddns.db'))


if __name__ == '__main__':
    unittest.main()
