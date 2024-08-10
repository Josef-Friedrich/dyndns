import subprocess


class TestCli:
    def test_help(self) -> None:
        out = subprocess.run(
            ["dyndns", "--help"], encoding="utf-8", stdout=subprocess.PIPE
        )
        assert out.returncode == 0
        assert out.stdout

    def test_version(self) -> None:
        out = subprocess.run(
            ["dyndns", "--version"], encoding="utf-8", stdout=subprocess.PIPE
        )
        assert out.returncode == 0
        assert out.stdout
