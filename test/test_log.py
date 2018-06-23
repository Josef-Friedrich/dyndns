from jfddns import log
from jfddns.log import UpdatesDB, DateTime
import os
import unittest
import datetime


def clean_log_file(log_file_path):
    log_file = open(log_file_path, 'w')
    log_file.write('')
    log_file.close()


class TestMethodMsg(unittest.TestCase):

    def setUp(self):
        self.log_file = log.log_file
        clean_log_file(self.log_file)

    def test_msg(self):
        self.assertEqual(log.msg('lol', 'UNCHANGED'), 'UNCHANGED: lol\n')

    def test_log_file(self):
        log.msg('lol', 'UNCHANGED')
        log_file = open(log.log_file, 'r')
        result = log_file.read()
        self.assertIn('UNCHANGED', result)
        self.assertIn('lol', result)


class TestClassDateTime(unittest.TestCase):

    def setUp(self):
        self.dt = DateTime('2018-06-23 07:49:58.694510')

    def test_init(self):
        self.assertEqual(str(self.dt.datetime), '2018-06-23 07:49:58.694510')

    def test_iso8601(self):
        self.assertEqual(self.dt.iso8601(), '2018-06-23 07:49:58.694510')

    def test_iso8601_short(self):
        self.assertEqual(self.dt.iso8601_short(), '2018-06-23 07:49:58')


class TestClassUpdateDB(unittest.TestCase):

    def _setup_test_db(self):
        db = UpdatesDB()
        db.log_update(True, 'c.example.com', 'a', '1.2.3.4')
        db.log_update(False, 'c.example.com', 'a', '1.2.3.4')
        db.log_update(True, 'c.example.com', 'a', '2.2.3.4')
        db.log_update(True, 'c.example.com', 'a', '3.2.3.4')
        db.log_update(True, 'c.example.com', 'aaaa', '1::2')
        db.log_update(True, 'c.example.com', 'aaaa', '1::3')
        db.log_update(True, 'b.example.com', 'a', '1.2.3.4')
        db.log_update(False, 'b.example.com', 'a', '1.2.3.4')
        db.log_update(True, 'a.example.com', 'a', '1.2.3.4')
        db.log_update(True, 'a.example.com', 'a', '1.2.3.3')
        db.log_update(True, 'a.example.com', 'a', '1.2.3.2')
        db.log_update(False, 'a.example.com', 'a', '1.2.3.2')
        return db

    def setUp(self):
        self.db_file = os.path.join(os.getcwd(), 'jfddns.db')
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    def test_init(self):
        db = UpdatesDB()
        self.assertEqual(db.db_file, self.db_file)

    def test_method_log_update(self):
        db = UpdatesDB()
        db.log_update(True, 'www.example.com', 'a', '1.2.3.4')

        db.cursor.execute('SELECT * FROM updates;')
        rows = db.cursor.fetchall()
        row = rows[0]
        dt = DateTime(row[0])
        self.assertEqual(dt.datetime.year, datetime.datetime.now().year)
        self.assertEqual(row[1], 1)
        self.assertEqual(row[2], 'www.example.com')
        self.assertEqual(row[3], 'a')
        self.assertEqual(row[4], '1.2.3.4')

        db.cursor.execute('SELECT fqdn FROM fqdns;')
        row = db.cursor.fetchone()
        self.assertEqual(row[0], 'www.example.com')

        # Add second entry
        db.log_update(True, 'www.example.com', 'a', '1.2.3.4')

        # fqdn gets entered only one time
        db.cursor.execute('SELECT fqdn FROM fqdns;')
        rows = db.cursor.fetchall()
        self.assertEqual(len(rows), 1)

        db.cursor.execute('SELECT * FROM updates;')
        rows = db.cursor.fetchall()
        self.assertEqual(len(rows), 2)

    def test_method_get_fqdns(self):
        db = self._setup_test_db()
        self.assertEqual(db.get_fqdns(),
                         ['a.example.com', 'b.example.com', 'c.example.com'])

    def test_method_is_fqdn_stored(self):
        db = UpdatesDB()
        self.assertFalse(db._is_fqdn_stored('example.com'))
        db.log_update(True, 'example.com', 'a', '1.2.3.2')
        self.assertTrue(db._is_fqdn_stored('example.com'))

    def test_method_get_updates_by_fqdn(self):
        db = self._setup_test_db()
        result = db.get_updates_by_fqdn('a.example.com')
        self.assertEqual(result[0][4], '1.2.3.4')

    def test_method_get_updates_by_fqdn_dict(self):
        db = self._setup_test_db()
        result = db.get_updates_by_fqdn_dict('a.example.com')
        self.assertTrue(result[0]['update_time'])
        self.assertEqual(result[0]['fqdn'], 'a.example.com')
        self.assertEqual(result[0]['record_type'], 'a')
        self.assertEqual(result[0]['ip'], '1.2.3.4')


if __name__ == '__main__':
    unittest.main()
