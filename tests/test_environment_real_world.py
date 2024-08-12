import pytest

from dyndns.environment import ConfiguredEnvironment

env = ConfiguredEnvironment("/etc/dyndns.yml")


@pytest.mark.skip
class TestClassZone:
    def test_delete(self) -> None:
        env.delete_dns_record("test.dyndns.friedrich.rocks")

    def test_add(self) -> None:
        env.delete_dns_record("test.dyndns.friedrich.rocks")
