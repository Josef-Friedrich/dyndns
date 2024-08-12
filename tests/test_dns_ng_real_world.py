import pytest

from dyndns.dns_ng import DnsZone
from dyndns.environment import ConfiguredEnvironment


@pytest.mark.skip
class TestClassDnsZone:
    dns: DnsZone

    def setup_method(self) -> None:
        env = ConfiguredEnvironment("/etc/dyndns.yml")

        self.dns = env.get_dns_for_zone("dyndns.friedrich.rocks")

    def test_add_record_by_type(self) -> None:
        self.dns.delete_record_by_type("test", "A")
        message = self.dns.add_record("test", 300, "A", "1.2.3.4")
        print(message.to_text())
        assert message.to_text() == 1

    def test_add_record_fqdn_by_type(self) -> None:
        self.dns.add_record("test.dyndns.friedrich.rocks", 300, "A", "1.2.3.4")

    def test_delete_record_by_type(self) -> None:
        self.dns.delete_record_by_type("test", "A")
