from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from dns.rrset import RRset
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from dyndns.config import Config
from dyndns.dns import DnsZone
from dyndns.environment import ConfiguredEnvironment
from dyndns.names import FullyQualifiedDomainName
from dyndns.types import RecordType
from dyndns.webapp import create_app
from dyndns.zones import Zone, ZonesCollection


@pytest.fixture
def env() -> ConfiguredEnvironment:
    return ConfiguredEnvironment(Path(__file__).parent / "files" / "dyndnsX.dev.yml")


@pytest.fixture
def config(env: ConfiguredEnvironment) -> Config:
    return env.config


@pytest.fixture
def zones(env: ConfiguredEnvironment) -> ZonesCollection:
    return env.zones


@pytest.fixture
def zone(zones: ZonesCollection) -> Zone:
    return zones.get_zone("dyndns1.dev")


@pytest.fixture
def dns(env: ConfiguredEnvironment) -> DnsZone:
    return env.get_dns_for_zone("dyndns1.dev")


@pytest.fixture
def fqdn(zones: ZonesCollection) -> FullyQualifiedDomainName:
    return FullyQualifiedDomainName(zones=zones, fqdn="test.dyndns1.dev")


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

    def __init__(self, client: FlaskClient, dns: DnsZone) -> None:
        self.client = client
        self.dns = dns
        self.dns.delete_records("test")

    def get(self, path: str) -> str:
        response: TestResponse = self.client.get(path)
        return response.data.decode()

    def get_response(self, path: str) -> TestResponse:
        return self.client.get(path)

    def add_record(self, name: str, record_type: RecordType, content: str) -> None:
        self.dns.add_record(name, record_type, content)

    def read_resource_record_set(
        self, name: str, record_type: RecordType
    ) -> RRset | None:
        return self.dns.read_resource_record_set(name, record_type)

    def read_record(self, name: str, record_type: RecordType) -> str | None:
        return self.dns.read_record(name, record_type)

    def delete_record(self, name: str, record_type: RecordType) -> None:
        self.dns.delete_record(name, record_type)


@pytest.fixture()
def client(flask_client: FlaskClient, dns: DnsZone) -> TestClient:
    return TestClient(flask_client, dns)
