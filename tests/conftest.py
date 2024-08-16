from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from dyndns.dns import DnsZone
from dyndns.environment import ConfiguredEnvironment
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
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
