import pytest
from dns.exception import SyntaxError

from dyndns.dns import DnsZone, validate_dns_name, validate_tsig_key
from dyndns.exceptions import DnsNameError


class TestFunctionValidateDnsName:
    def assert_raises_msg(self, hostname: str, msg: str) -> None:
        with pytest.raises(DnsNameError, match=msg):
            validate_dns_name(hostname)

    def test_valid(self) -> None:
        assert validate_dns_name("www.example.com") == "www.example.com."

    def test_invalid_tld(self) -> None:
        self.assert_raises_msg(
            "www.example.777",
            'The TLD "777" of the DNS name "www.example.777" must be not all-numeric.',
        )

    def test_invalid_to_long(self) -> None:
        self.assert_raises_msg(
            "a" * 300,
            'The DNS name "aaaaaaaaaa..." is longer than 253 characters.',
        )

    def test_invalid_characters(self) -> None:
        self.assert_raises_msg(
            "www.exämple.com",
            'The label "exämple" of the hostname "www.exämple.com" is invalid.',
        )


class TestFunctionValidateTsigKey:
    def assert_raises_msg(self, tsig_key: str, message: str) -> None:
        with pytest.raises(DnsNameError, match=message):
            validate_tsig_key(tsig_key)

    def test_valid(self) -> None:
        assert validate_tsig_key("tPyvZA==") == "tPyvZA=="

    def test_invalid_empty(self) -> None:
        self.assert_raises_msg("", 'Invalid tsig key: "".')

    def test_invalid_string(self) -> None:
        self.assert_raises_msg("xxx", 'Invalid tsig key: "xxx".')


def test_class_dns_change_message(dns: DnsZone) -> None:
    dns.add_record("record", "A", "1.2.3.4")
    message = dns.add_record("record", "A", "1.2.3.5")
    assert message.fqdn == "record.dyndns1.dev."
    assert message.old == "1.2.3.4"
    assert message.new == "1.2.3.5"
    assert message.record_type == "A"
    assert message.changed is True


class TestClassDnsZone:
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
            dns.add_record("test.dyndns1.dev", "A", "1.2.3.5")
            answer: str | None = dns.read_record("test", "A")
            assert answer
            assert answer == "1.2.3.5"

        def test_txt_record(self, dns: DnsZone) -> None:
            dns.delete_record("txt", "TXT")
            dns.add_record("txt.dyndns1.dev", "TXT", "STRING")
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

    def test_read_a_record(self, dns: DnsZone) -> None:
        dns.add_record("a.record.test", "A", "1.1.1.1")
        ip: str | None = dns.read_a_record("a.record.test")
        assert ip == "1.1.1.1"
        dns.delete_record("a.record.test", "A")

    def test_read_aaaa_record(self, dns: DnsZone) -> None:
        dns.add_record("aaaa.record.test", "AAAA", "1::2")
        ip: str | None = dns.read_aaaa_record("aaaa.record.test")
        assert ip == "1::2"
        dns.delete_record("aaaa.record.test", "AAAA")

    class TestDeleteRecord:
        def test_existent(self, dns: DnsZone) -> None:
            dns.add_record("test", "A", "7.7.7.7")
            message = dns.delete_record("test", "A")
            assert message.old == "7.7.7.7"
            assert message.new is None
            assert message.record_type == "A"
            ip: str | None = dns.read_a_record("test")
            assert ip is None

        def test_non_existent(self, dns: DnsZone) -> None:
            dns.delete_record("test", "A")
            message = dns.delete_record("test", "A")
            assert message.old is None
            assert message.new is None
            assert message.record_type == "A"
            ip: str | None = dns.read_a_record("test")
            assert ip is None
