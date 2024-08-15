import pytest
from dns.exception import SyntaxError
from dns.rrset import RRset

from dyndns.dns_ng import DnsZone
from dyndns.environment import ConfiguredEnvironment
from tests._helper import NOT_REAL_WORLD


@pytest.fixture
def env() -> ConfiguredEnvironment:
    return ConfiguredEnvironment("/etc/dyndns.yml")


@pytest.fixture
def dns(env: ConfiguredEnvironment) -> DnsZone:
    return env.get_dns_for_zone("dyndns.friedrich.rocks")


@pytest.mark.skipif(NOT_REAL_WORLD, reason="No DNS server configured.")
class TestAddRecord:
    def test_specified_as_record_name(self, dns: DnsZone) -> None:
        dns.delete_record_by_type("test", "A")
        dns.add_record("test", 300, "A", "1.2.3.4")
        ip: str | None = dns.read_a_record("test")
        assert ip == "1.2.3.4"
        dns.delete_record_by_type("test", "A")

    def test_specified_as_fqdn(self, dns: DnsZone) -> None:
        dns.add_record("test.dyndns.friedrich.rocks", 300, "A", "1.2.3.5")
        answer: RRset | None = dns.read_record("test", "A")
        assert answer
        assert str(answer[0]) == "1.2.3.5"  # type: ignore

    def test_invalid_a_ip_address(self, dns: DnsZone) -> None:
        with pytest.raises(SyntaxError, match="Text input is malformed."):
            dns.add_record("test", 300, "A", "invalid")

    def test_invalid_aaaa_ip_address(self, dns: DnsZone) -> None:
        with pytest.raises(SyntaxError, match="Text input is malformed."):
            dns.add_record("test", 300, "AAAA", "invalid")


@pytest.mark.skipif(NOT_REAL_WORLD, reason="No DNS server configured.")
def test_read_a_record(dns: DnsZone) -> None:
    dns.add_record("a.record.test", 300, "A", "1.1.1.1")
    ip: str | None = dns.read_a_record("a.record.test")
    assert ip == "1.1.1.1"
    dns.delete_record_by_type("a.record.test", "A")


@pytest.mark.skipif(NOT_REAL_WORLD, reason="No DNS server configured.")
def test_read_aaaa_record(dns: DnsZone) -> None:
    dns.add_record("aaaa.record.test", 300, "AAAA", "1::2")
    ip: str | None = dns.read_aaaa_record("aaaa.record.test")
    assert ip == "1::2"
    dns.delete_record_by_type("a.record.test", "A")


@pytest.mark.skipif(NOT_REAL_WORLD, reason="No DNS server configured.")
def test_delete_record_by_type(dns: DnsZone) -> None:
    dns.delete_record_by_type("test", "A")
    ip: str | None = dns.read_a_record("test")
    assert ip is None
