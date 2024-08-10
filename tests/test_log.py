from dyndns.log import LogLevel, logger


class TestLogger:
    def test_log(self) -> None:
        assert logger.log(LogLevel.UNCHANGED, "lol") == "UNCHANGED: lol\n"
