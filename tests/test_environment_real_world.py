import pytest

from dyndns.environment import ConfiguredEnvironment
from tests._helper import NOT_REAL_WORLD


@pytest.mark.skipif(NOT_REAL_WORLD, reason="No DNS server configured.")
class TestClassZone:
    def test_delete_unchanged(self, env: ConfiguredEnvironment) -> None:
        env.delete_dns_record("test.dyndns1.dev")
        assert (
            env.delete_dns_record("test.dyndns1.dev")
            == 'UNCHANGED: The deletion of the domain name "test.dyndns1.dev." was not executed because there were no A or AAAA records.\n'
        )

    def test_delete(self, env: ConfiguredEnvironment) -> None:
        env.update_dns_record(fqdn="test.dyndns1.dev", ip_1="1.2.3.4", ip_2="1:2:3::4")

        assert (
            env.delete_dns_record("test.dyndns1.dev")
            == 'UPDATED: The A and AAAA records of the domain name "test.dyndns1.dev." were deleted.\n'
        )

    def test_add(self, env: ConfiguredEnvironment) -> None:
        env.delete_dns_record("test.dyndns1.dev")
