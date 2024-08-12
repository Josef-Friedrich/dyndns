import pytest

from dyndns.environment import ConfiguredEnvironment

env = ConfiguredEnvironment("/etc/dyndns.yml")

dns = env.get_dns_for_zone("dyndns.friedrich.rocks")


@pytest.mark.skip
class TestClassDnsZone:
    def test_add_record_by_type(self) -> None:
        dns.delete_record_by_type("test", "A")
        message = dns.add_record("test", 300, "A", "1.2.3.4")
        print(message.to_text())
        assert message.to_text() == 1

    def test_add_record_fqdn_by_type(self) -> None:
        dns.add_record("test.dyndns.friedrich.rocks", 300, "A", "1.2.3.4")

    def test_delete_record_by_type(self) -> None:
        dns.delete_record_by_type("test", "A")
