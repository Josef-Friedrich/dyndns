import pytest
from dns.name import EmptyLabel, LabelTooLong, NameTooLong

from dyndns.names import FullyQualifiedDomainName, validate_name
from tests._helper import zones


class TestValidateName:
    def test_dot_is_appended(self) -> None:
        assert validate_name("www.example.com") == "www.example.com."

    def test_numbers(self) -> None:
        assert validate_name("123.123.123") == "123.123.123."

    def test_spaces(self) -> None:
        with pytest.raises(EmptyLabel, match="A DNS label is empty."):
            validate_name("www..com")

    def test_label_to_long(self) -> None:
        with pytest.raises(LabelTooLong, match="A DNS label is > 63 octets long."):
            validate_name(
                "to.looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong.com"
            )

    def test_to_long(self) -> None:
        with pytest.raises(NameTooLong):
            validate_name("abcdefghij." * 24)


class TestClassFullyQualifiedDomainName:
    fqdn: FullyQualifiedDomainName

    def setup_method(self) -> None:
        self.fqdn = FullyQualifiedDomainName(zones=zones, fqdn="www.example.com")

    def test_attribute_fqdn(self) -> None:
        assert self.fqdn.fqdn == "www.example.com."

    def test_attribute_zone_name(self) -> None:
        assert self.fqdn.zone_name == "example.com."

    def test_attribute_record_name(self) -> None:
        assert self.fqdn.record_name == "www."

    def test_attribute_tsig_key(self) -> None:
        assert self.fqdn.tsig_key == "tPyvZA=="
