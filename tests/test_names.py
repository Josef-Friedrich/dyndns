from dyndns.names import FullyQualifiedDomainName


def test_attribute_fqdn(fqdn: FullyQualifiedDomainName) -> None:
    assert fqdn.fqdn == "test.dyndns1.dev."


def test_attribute_zone_name(fqdn: FullyQualifiedDomainName) -> None:
    assert fqdn.zone_name == "dyndns1.dev."


def test_attribute_record_name(fqdn: FullyQualifiedDomainName) -> None:
    assert fqdn.record_name == "test."


def test_attribute_tsig_key(fqdn: FullyQualifiedDomainName) -> None:
    assert (
        fqdn.tsig_key
        == "aaZI/Ssod3/yqhknm85T3IPKScEU4Q/CbQ2J+QQW9IXeLwkLkxFprkYDoHqre4ECqTfgeu/34DCjHJO8peQc/g=="
    )
