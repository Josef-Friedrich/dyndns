import pytest
from dns.exception import SyntaxError

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
        dns.delete_record("test", "A")
        dns.add_record("test", "A", "1.2.3.4")
        ip: str | None = dns.read_a_record("test")
        assert ip == "1.2.3.4"
        dns.delete_record("test", "A")

    def test_update(self, dns: DnsZone) -> None:
        dns.delete_record("test", "A")
        dns.add_record("test", "A", "1.2.3.1")
        update = dns.add_record("test", "A", "1.2.3.2")
        assert update.old == "1.2.3.1"
        assert update.new == "1.2.3.2"
        dns.delete_record("test", "A")

    def test_add_multiple(self, dns: DnsZone) -> None:
        dns.delete_record("test", "A")
        dns.add_record("test", "A", "1.2.3.1")
        dns.add_record("test", "A", "2.2.3.2")
        dns.add_record("test", "A", "3.2.3.3")
        dns.add_record("test", "A", "4.2.3.4")
        dns.delete_record("test", "A")

    def test_specified_as_fqdn(self, dns: DnsZone) -> None:
        dns.add_record("test.dyndns.friedrich.rocks", "A", "1.2.3.5")
        answer: str | None = dns.read_record("test", "A")
        assert answer
        assert answer == "1.2.3.5"

    def test_txt_record(self, dns: DnsZone) -> None:
        dns.delete_record("txt", "TXT")
        dns.add_record("txt.dyndns.friedrich.rocks", "TXT", "STRING")
        answer: str | None = dns.read_record("txt", "TXT")
        assert answer
        assert answer == "STRING"
        dns.delete_record("txt", "TXT")

    def test_invalid_a_ip_address(self, dns: DnsZone) -> None:
        with pytest.raises(SyntaxError, match="Text input is malformed."):
            dns.add_record("test", "A", "invalid")

    def test_invalid_aaaa_ip_address(self, dns: DnsZone) -> None:
        with pytest.raises(SyntaxError, match="Text input is malformed."):
            dns.add_record("test", "AAAA", "invalid")


@pytest.mark.skipif(NOT_REAL_WORLD, reason="No DNS server configured.")
def test_read_a_record(dns: DnsZone) -> None:
    dns.add_record("a.record.test", "A", "1.1.1.1")
    ip: str | None = dns.read_a_record("a.record.test")
    assert ip == "1.1.1.1"
    dns.delete_record("a.record.test", "A")


@pytest.mark.skipif(NOT_REAL_WORLD, reason="No DNS server configured.")
def test_read_aaaa_record(dns: DnsZone) -> None:
    dns.add_record("aaaa.record.test", "AAAA", "1::2")
    ip: str | None = dns.read_aaaa_record("aaaa.record.test")
    assert ip == "1::2"
    dns.delete_record("aaaa.record.test", "AAAA")


@pytest.mark.skipif(NOT_REAL_WORLD, reason="No DNS server configured.")
def test_delete_record_by_type(dns: DnsZone) -> None:
    dns.delete_record("test", "A")
    ip: str | None = dns.read_a_record("test")
    assert ip is None