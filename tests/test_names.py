from dyndns.names import (
    FullyQualifiedDomainName,
)
from tests._helper import zones


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
