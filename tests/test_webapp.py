import os
from typing import Any, Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from dyndns.webapp import app
from tests import _helper


@pytest.fixture()
def run_app() -> Generator[Flask, Any, None]:
    os.environ["dyndns_CONFIG_FILE"] = _helper.config_file
    app.config["TESTING"] = True
    yield app


@pytest.fixture()
def client(run_app: Flask) -> FlaskClient:
    return run_app.test_client()


def test_home(client: FlaskClient) -> None:
    response: TestResponse = client.get("/")
    assert b"dyndns" in response.data


def test_wrong_secret(client: FlaskClient) -> None:
    response: TestResponse = client.get(
        "/update-by-path/wrong-secret/test.example.com/1.2.3.4"
    )
    assert response.status_code == 456
    assert b"ParameterError: You specified a wrong secret key." in response.data


def test_wrong_fqdn(client: FlaskClient) -> None:
    response: TestResponse = client.get(
        "/update-by-path/12345678/test.wrong-domain.de/1.2.3.4"
    )
    assert response.status_code == 456
    assert (
        b'ParameterError: The fully qualified domain name "test.wrong-domain.de." could not be split into a record and a zone name.'
        in response.data
    )


def test_wrong_ip(client: FlaskClient) -> None:
    response: TestResponse = client.get(
        "/update-by-path/12345678/test.example.com/1.2.3"
    )
    assert response.status_code == 456
    assert b'ParameterError: Invalid ip address "1.2.3"' in response.data
