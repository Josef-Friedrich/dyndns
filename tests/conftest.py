from pathlib import Path

import pytest

from dyndns.dns_ng import DnsZone
from dyndns.environment import ConfiguredEnvironment


@pytest.fixture
def env() -> ConfiguredEnvironment:
    return ConfiguredEnvironment(Path(__file__).parent / "files" / "dyndnsX.dev.yml")


@pytest.fixture
def dns(env: ConfiguredEnvironment) -> DnsZone:
    return env.get_dns_for_zone("dyndns1.dev")
