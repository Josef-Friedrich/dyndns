from dyndns.environment import ConfiguredEnvironment


class TestClassConfiguredEnvironment:
    def test_update_dns_record(self, env: ConfiguredEnvironment) -> None:
        env.update_dns_record(fqdn="test.dyndns1.dev", ip_1="1.2.3.4")
        assert (
            env.update_dns_record(fqdn="test.dyndns1.dev", ip_1="9.8.7.6")
            == "UPDATED: test.dyndns1.dev. A 1.2.3.4 -> 9.8.7.6\n"
            + "UNCHANGED: test.dyndns1.dev. AAAA None\n"
        )

    class TestMethodeDeleteDnsRecord:
        def test_updated(self, env: ConfiguredEnvironment) -> None:
            env.update_dns_record(
                fqdn="test.dyndns1.dev", ip_1="1.2.3.4", ip_2="1:2:3::4"
            )
            assert (
                env.delete_dns_record("test.dyndns1.dev")
                == "UPDATED: The A and AAAA records of the domain name 'test.dyndns1.dev.' were deleted.\n"
            )

        def test_unchanged(self, env: ConfiguredEnvironment) -> None:
            env.delete_dns_record("test.dyndns1.dev")
            assert (
                env.delete_dns_record("test.dyndns1.dev")
                == "UNCHANGED: The deletion of the domain name 'test.dyndns1.dev.' was not executed because there were no A or AAAA records.\n"
            )
