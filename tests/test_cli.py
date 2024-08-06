import subprocess
import unittest


class TestCli:
    def test_help(self):
        out = subprocess.run(
            ["dyndns-debug", "--help"], encoding="utf-8", stdout=subprocess.PIPE
        )
        assert out.returncode == 0
        assert out.stdout

    def test_version(self):
        out = subprocess.run(
            ["dyndns-debug", "--version"], encoding="utf-8", stdout=subprocess.PIPE
        )
        assert out.returncode == 0
        assert out.stdout
