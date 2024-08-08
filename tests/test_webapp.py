from typing import Any, Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from dyndns.webapp import app

app.config["TESTING"] = True


@pytest.fixture()
def run_app() -> Generator[Flask, Any, None]:
    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture()
def client(run_app: Flask) -> FlaskClient:
    return run_app.test_client()


@pytest.fixture()
def runner(run_app: Flask) -> FlaskCliRunner:
    return run_app.test_cli_runner()


def test_home(client: FlaskClient) -> None:
    response = client.get("/")
    assert b"dyndns" in response.data
