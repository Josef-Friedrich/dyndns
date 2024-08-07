from dyndns.log import DateTime, log_file, logger


def clean_log_file(log_file_path: str) -> None:
    log_file = open(log_file_path, "w")
    log_file.write("")
    log_file.close()


class TestMethodMsg:
    def setup_method(self) -> None:
        clean_log_file(log_file)

    def test_msg(self) -> None:
        assert logger.log("lol", "UNCHANGED") == "UNCHANGED: lol\n"

    def test_log_file(self) -> None:
        logger.log("lol", "UNCHANGED")
        file = open(log_file, "r")
        result = file.read()
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
