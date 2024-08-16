from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from flask import Flask
from flask.testing import FlaskClient

from dyndns.dns import DnsZone
from dyndns.environment import ConfiguredEnvironment
from dyndns.types import RecordType
from dyndns.webapp import create_app


@pytest.fixture
def env() -> ConfiguredEnvironment:
    return ConfiguredEnvironment(Path(__file__).parent / "files" / "dyndnsX.dev.yml")


@pytest.fixture
def dns(env: ConfiguredEnvironment) -> DnsZone:
    return env.get_dns_for_zone("dyndns1.dev")


@pytest.fixture()
def app(env: ConfiguredEnvironment) -> Generator[Flask, Any, None]:
    app: Flask = create_app(env)
    app.config.update(  # type: ignore
        {
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture()
def flask_client(app: Flask) -> FlaskClient:
    return app.test_client()


class TestClient:
    __test__ = False

    client: FlaskClient

    dns: DnsZone

    def __init__(self, client: FlaskClient, dns: DnsZone):
        self.client = client
        self.dns = dns

    def get(self, path: str) -> str:
        response = self.client.get(path)
        return response.data.decode()

    def add_record(self, name: str, record_type: RecordType, content: str) -> None:
        self.dns.add_record(name, record_type, content)

    def delete_record(self, name: str, record_type: RecordType) -> None:
        self.dns.delete_record(name, record_type)


@pytest.fixture()
def client(flask_client: FlaskClient, dns: DnsZone) -> TestClient:
    return TestClient(flask_client, dns)
