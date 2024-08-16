import os
from typing import Any
from unittest import mock

import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from dyndns.environment import ConfiguredEnvironment
from dyndns.webapp import create_app
from tests import _helper


class TestIntegration:
    app: FlaskClient

    mock_tcp: mock.Mock
    """Mocks ``dns.query.tcp``."""

    mock_Update: mock.Mock
    """Mocks ``dns.update.Update``."""

    mock_Resolver: mock.Mock
    """Mocks ``dns.resolver.Resolver``."""

    mock_resolver: mock.Mock
    """Mocks ``resolver = Resolver()``."""

    response: TestResponse

    data: str
    """``response.data.decode("utf-8")``"""

    mock_update: mock.Mock

    def setup_method(self) -> None:
        os.environ["dyndns_CONFIG_FILE"] = _helper.config_file
        app = create_app(ConfiguredEnvironment())
        app.config["TESTING"] = True
        self.app = app.test_client()

    def get(self, path: str, side_effect: Any = None) -> TestResponse:
        with mock.patch("dns.query.tcp") as tcp, mock.patch(
            "dns.update.Update"
        ) as Update, mock.patch("dns.resolver.Resolver") as Resolver:
            self.mock_tcp = tcp
            self.mock_Update = Update
            self.mock_Resolver = Resolver
            self.mock_resolver = self.mock_Resolver.return_value
            if side_effect:
                self.mock_resolver.resolve.side_effect = side_effect
            self.response = self.app.get(path)
            self.data = self.response.data.decode("utf-8")
            self.mock_update = Update.return_value
            return self.response


class TestMethodUpdateByPath(TestIntegration):
    @pytest.mark.skip
    @mock.patch("dyndns.webapp.update_dns_record")
    def test_call_secret_fqdn(self, update: mock.Mock) -> None:
        update.return_value = "ok"
        self.app.get("/update-by-path/secret/fqdn")
        update.assert_called_with(secret="secret", fqdn="fqdn", ip_1=None, ip_2=None)

    @pytest.mark.skip
    @mock.patch("dyndns.webapp.update_dns_record")
    def test_call_secret_fqdn_ip_1(self, update: mock.Mock) -> None:
        update.return_value = "ok"
        self.app.get("/update-by-path/secret/fqdn/ip_1")
        update.assert_called_with(secret="secret", fqdn="fqdn", ip_1="ip_1", ip_2=None)

    @pytest.mark.skip
    @mock.patch("dyndns.webapp.update_dns_record")
    def test_call_secret_fqdn_ip1_ip2(self, update: mock.Mock) -> None:
        update.return_value = "ok"
        self.app.get("/update-by-path/secret/fqdn/ip_1/ip_2")
        update.assert_called_with(
            secret="secret", fqdn="fqdn", ip_1="ip_1", ip_2="ip_2"
        )


class TestUpdateByPath(TestIntegration):
    """Test the path ``update-by-path`` of the Flask web app."""

    @staticmethod
    def _url(path: str) -> str:
        return f"/update-by-path/12345678/www.example.com/{path}"

    @pytest.mark.skip
    def test_ipv4_update(self) -> None:
        self.get(self._url("1.2.3.5"), [["1.2.3.4"], ["1.2.3.5"]])

        self.mock_update.delete.assert_has_calls(
            [
                mock.call("www.example.com.", "A"),
                mock.call("www.example.com.", "AAAA"),
            ]
        )
        self.mock_update.add.assert_called_with("www.example.com.", 300, "A", "1.2.3.5")
        assert (
            self.data == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: "
            "1.2.3.5\n"
        )

    @pytest.mark.skip
    def test_ipv6_update(self) -> None:
        self.get(self._url("1::3"), [["1::2"], ["1::3"]])
        self.mock_update.delete.assert_called_with("www.example.com.", "AAAA")
        self.mock_update.add.assert_called_with("www.example.com.", 300, "AAAA", "1::3")
        assert (
            self.data == "UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n"
        )

    @pytest.mark.skip
    def test_ipv4_ipv6_update(self) -> None:
        self.get(
            self._url("1.2.3.5/1::3"), [["1.2.3.4"], ["1.2.3.5"], ["1::2"], ["1::3"]]
        )
        self.mock_update.delete.assert_called_with("www.example.com.", "AAAA")
        self.mock_update.add.assert_called_with("www.example.com.", 300, "AAAA", "1::3")
        assert (
            self.data
            == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5\n"
            "UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n"
        )

    @pytest.mark.skip
    def test_ipv6_ipv4_update(self) -> None:
        self.get(
            self._url("1::3/1.2.3.5"), [["1.2.3.4"], ["1.2.3.5"], ["1::2"], ["1::3"]]
        )
        self.mock_update.delete.assert_called_with("www.example.com.", "AAAA")
        self.mock_update.add.assert_called_with("www.example.com.", 300, "AAAA", "1::3")
        assert (
            self.data
            == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5\n"
            "UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n"
        )

    def test_wrong_secret(self) -> None:
        self.get("/update-by-path/wrong-secret/test.example.com/1.2.3.4")
        assert self.response.status_code == 456
        assert (
            b"PARAMETER_ERROR: You specified a wrong secret key." in self.response.data
        )

    def test_wrong_fqdn(self) -> None:
        self.get("/update-by-path/12345678/test.wrong-domain.de/1.2.3.4")
        assert self.response.status_code == 453
        assert (
            b'DNS_NAME_ERROR: The fully qualified domain name "test.wrong-domain.de." could not be split into a record and a zone name.\n'
            in self.response.data
        )

    def test_wrong_ip(self) -> None:
        self.get("/update-by-path/12345678/test.example.com/1.2.3")
        assert self.response.status_code == 454
        assert b'IP_ADDRESS_ERROR: Invalid ip address "1.2.3"\n' in self.response.data


class TestUpdateByQuery(TestIntegration):
    """Test the path ``update-by-query`` of the Flask web app."""

    @staticmethod
    def _url(query_string: str) -> str:
        return (
            "/update-by-query?secret=12345678&record_name=www&zone_name="
            f"example.com&{query_string}"
        )

    @pytest.mark.skip
    def test_unkown_argument(self) -> None:
        self.get("/update-by-query?unknown=unknown")
        assert (
            self.data == 'PARAMETER_ERROR: Unknown query string argument: "unknown"\n'
        )

    @pytest.mark.skip
    def test_ipv4_update(self) -> None:
        side_effect = [["1.2.3.4"], ["1.2.3.5"]]
        self.get(self._url("ipv4=1.2.3.5"), side_effect)

        self.mock_update.delete.assert_has_calls(
            [
                mock.call("www.example.com.", "A"),
                mock.call("www.example.com.", "AAAA"),
            ]
        )
        self.mock_update.add.assert_called_with("www.example.com.", 300, "A", "1.2.3.5")
        assert (
            self.data == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: "
            "1.2.3.5\n"
        )

    @pytest.mark.skip
    def test_ipv6_update(self) -> None:
        side_effect = [["1::2"], ["1::3"]]
        self.get(self._url("ipv6=1::3"), side_effect)
        self.mock_update.delete.assert_called_with("www.example.com.", "AAAA")
        self.mock_update.add.assert_called_with("www.example.com.", 300, "AAAA", "1::3")
        assert (
            self.data == "UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n"
        )

    @pytest.mark.skip
    def test_ipv4_ipv6_update(self) -> None:
        side_effect = [["1.2.3.4"], ["1.2.3.5"], ["1::2"], ["1::3"]]
        self.get(self._url("ipv4=1.2.3.5&ipv6=1::3"), side_effect)
        assert (
            self.data
            == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5\n"
            "UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n"
        )

    @pytest.mark.skip
    def test_ip_1_ip_2_update(self) -> None:
        side_effect = [["1.2.3.4"], ["1.2.3.5"], ["1::2"], ["1::3"]]
        self.get(self._url("ip_1=1.2.3.5&ip_2=1::3"), side_effect)
        assert (
            self.data
            == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5\n"
            "UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n"
        )

    def test_invalid_ipv4(self) -> None:
        self.get(self._url("ipv4=1.2.3.4.5"))
        assert self.data == 'IP_ADDRESS_ERROR: Invalid ip address "1.2.3.4.5"\n'

    @pytest.mark.skip
    def test_ttl(self) -> None:
        side_effect = [["1.2.3.4"], ["1.2.3.5"]]
        self.get(self._url("ipv4=1.2.3.5&ttl=123"), side_effect)
        self.mock_update.add.assert_called_with("www.example.com.", 123, "A", "1.2.3.5")


class TestDeleteByPath(TestIntegration):
    @staticmethod
    def _url(fqdn: str) -> str:
        return f"/delete-by-path/12345678/{fqdn}"

    @pytest.mark.skip
    def test_deletion(self) -> None:
        self.get(self._url("www.example.com"))

        self.mock_update.delete.assert_has_calls(
            [
                mock.call("www.example.com.", "A"),
                mock.call("www.example.com.", "AAAA"),
            ]
        )
        self.mock_update.add.assert_not_called()
        assert self.data == 'UPDATED: Deleted "www.example.com.".\n'


class TestMultiplePaths(TestIntegration):
    def test_home(self, client: FlaskClient) -> None:
        response = client.get("/")
        assert b"dyndns" in response.data

    def test_check(self, client: FlaskClient) -> None:
        response = client.get("/check")
        content = response.data.decode()
        assert "could be updated on the zone 'dyndns1.dev.'" in content
        assert "could be updated on the zone 'dyndns2.dev.'" in content
