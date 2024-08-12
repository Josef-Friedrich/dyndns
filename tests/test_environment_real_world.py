import pytest

from dyndns.environment import ConfiguredEnvironment


@pytest.mark.skip
class TestClassZone:
    env: ConfiguredEnvironment

    def setup_method(self):
        self.env = ConfiguredEnvironment("/etc/dyndns.yml")

    def test_delete(self) -> None:
        self.env.delete_dns_record("test.dyndns.friedrich.rocks")

    def test_add(self) -> None:
        self.env.delete_dns_record("test.dyndns.friedrich.rocks")
