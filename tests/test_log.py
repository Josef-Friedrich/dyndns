import datetime
import unittest

import _helper

from dyndns import log
from dyndns.log import DateTime, UpdatesDB


def clean_log_file(log_file_path: str) -> None:
    log_file = open(log_file_path, "w")
    log_file.write("")
    log_file.close()


class TestMethodMsg:
    def setup_method(self) -> None:
        self.log_file = log.log_file
        clean_log_file(self.log_file)

    def test_msg(self) -> None:
        assert log.msg("lol", "UNCHANGED") == "UNCHANGED: lol\n"

    def test_log_file(self) -> None:
        log.msg("lol", "UNCHANGED")
        log_file = open(log.log_file, "r")
        result = log_file.read()
        assert "UNCHANGED" in result
        assert "lol" in result


class TestClassDateTime:
    def setup_method(self) -> None:
        self.dt = DateTime("2018-06-23 07:49:58.694510")

    def test_init(self) -> None:
        assert str(self.dt.datetime) == "2018-06-23 07:49:58.694510"

    def test_iso8601(self) -> None:
        assert self.dt.iso8601() == "2018-06-23 07:49:58.694510"

    def test_iso8601_short(self) -> None:
        assert self.dt.iso8601_short() == "2018-06-23 07:49:58"


class TestClassUpdateDB:
    def setup_method(self) -> None:
        _helper.remove_updates_db()

    def test_init(self) -> None:
        db = UpdatesDB()
        assert db.db_file

    def test_method_log_update(self) -> None:
        db = UpdatesDB()
        db.log_update(True, "www.example.com", "a", "1.2.3.4")

        db.cursor.execute("SELECT * FROM updates;")
        rows = db.cursor.fetchall()
        row = rows[0]
        dt = DateTime(row[0])
        assert dt.datetime.year == datetime.datetime.now().year
        assert row[1] == 1
        assert row[2] == "www.example.com"
        assert row[3] == "a"
        assert row[4] == "1.2.3.4"

        db.cursor.execute("SELECT fqdn FROM fqdns;")
        row = db.cursor.fetchone()
        assert row[0] == "www.example.com"

        # Add second entry
        db.log_update(True, "www.example.com", "a", "1.2.3.4")

        # fqdn gets entered only one time
        db.cursor.execute("SELECT fqdn FROM fqdns;")
        rows = db.cursor.fetchall()
        assert len(rows) == 1

        db.cursor.execute("SELECT * FROM updates;")
        rows = db.cursor.fetchall()
        assert len(rows) == 2

    def test_method_get_fqdns(self):
        db = _helper.get_updates_db()
        assert db.get_fqdns() == ["a.example.com", "b.example.com", "c.example.com"]

    def test_method_is_fqdn_stored(self):
        db = UpdatesDB()
        assert not db._is_fqdn_stored("example.com")
        db.log_update(True, "example.com", "a", "1.2.3.2")
        assert db._is_fqdn_stored("example.com")

    def test_method_get_updates_by_fqdn(self):
        db = _helper.get_updates_db()
        result = db.get_updates_by_fqdn("a.example.com")
        assert result[0]["update_time"]
        assert result[0]["fqdn"] == "a.example.com"
        assert result[0]["record_type"] == "a"
        assert result[0]["ip"] == "1.2.3.4"


if __name__ == "__main__":
    unittest.main()
