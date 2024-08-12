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
        self.dns.add_record("test", 300, "A", "1.2.3.4")
        ip = self.dns.read_a_record("test")
        assert ip == "1.2.3.4"
        self.dns.delete_record_by_type("test", "A")

    def test_add_record_fqdn_by_type(self) -> None:
        self.dns.add_record("test.dyndns.friedrich.rocks", 300, "A", "1.2.3.4")
        answer = self.dns.read_record("test.dyndns.friedrich.rocks", "A")
        assert answer
        assert str(answer[0]) == "1.2.3.4"  # type: ignore

    def test_read_a_record(self) -> None:
        self.dns.add_record("a.record.test", 300, "A", "1.1.1.1")
        ip = self.dns.read_a_record("a.record.test")
        assert ip == "1.1.1.1"
        self.dns.delete_record_by_type("a.record.test", "A")

    def test_delete_record_by_type(self) -> None:
        self.dns.delete_record_by_type("test", "A")
        ip = self.dns.read_a_record("test")
        assert ip is None
