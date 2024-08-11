import os
from typing import Any
from unittest import mock

import pytest
from dns.rdataclass import RdataClass
from dns.rdatatype import RdataType
from dns.rdtypes.ANY.TXT import TXT
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from dyndns.webapp import app
from tests import _helper

app.config["TESTING"] = True


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

    mock_update: mock.Mock

    def setup_method(self) -> None:
        os.environ["dyndns_CONFIG_FILE"] = _helper.config_file
        self.app = app.test_client()

    def get(self, path: str, side_effect: Any = None) -> None:
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


class TestMethodUpdateByPath:
    def setup_method(self) -> None:
        self.app = app.test_client()

    @mock.patch("dyndns.webapp.update_dns_record")
    def test_call_secret_fqdn(self, update: mock.Mock) -> None:
        update.return_value = "ok"
        self.app.get("/update-by-path/secret/fqdn")
        update.assert_called_with(secret="secret", fqdn="fqdn", ip_1=None, ip_2=None)

    @mock.patch("dyndns.webapp.update_dns_record")
    def test_call_secret_fqdn_ip_1(self, update: mock.Mock) -> None:
        update.return_value = "ok"
        self.app.get("/update-by-path/secret/fqdn/ip_1")
        update.assert_called_with(secret="secret", fqdn="fqdn", ip_1="ip_1", ip_2=None)

    @mock.patch("dyndns.webapp.update_dns_record")
    def test_call_secret_fqdn_ip1_ip2(self, update: mock.Mock) -> None:
        update.return_value = "ok"
        self.app.get("/update-by-path/secret/fqdn/ip_1/ip_2")
        update.assert_called_with(
            secret="secret", fqdn="fqdn", ip_1="ip_1", ip_2="ip_2"
        )


class TestUpdateByPath(TestIntegration):
    @staticmethod
    def _url(path: str) -> str:
        return f"/update-by-path/12345678/www.example.com/{path}"

    def test_ipv4_update(self) -> None:
        self.get(self._url("1.2.3.5"), [["1.2.3.4"], ["1.2.3.5"]])

        self.mock_update.delete.assert_has_calls(
            [
                mock.call("www.example.com.", "a"),
                mock.call("www.example.com.", "aaaa"),
            ]
        )
        self.mock_update.add.assert_called_with("www.example.com.", 300, "a", "1.2.3.5")
        assert (
            self.data == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: "
            "1.2.3.5\n"
        )

    def test_ipv6_update(self) -> None:
        self.get(self._url("1::3"), [["1::2"], ["1::3"]])
        self.mock_update.delete.assert_called_with("www.example.com.", "aaaa")
        self.mock_update.add.assert_called_with("www.example.com.", 300, "aaaa", "1::3")
        assert (
            self.data == "UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n"
        )

    def test_ipv4_ipv6_update(self) -> None:
        self.get(
            self._url("1.2.3.5/1::3"), [["1.2.3.4"], ["1.2.3.5"], ["1::2"], ["1::3"]]
        )
        self.mock_update.delete.assert_called_with("www.example.com.", "aaaa")
        self.mock_update.add.assert_called_with("www.example.com.", 300, "aaaa", "1::3")
        assert (
            self.data
            == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5\n"
            "UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n"
        )

    def test_ipv6_ipv4_update(self) -> None:
        self.get(
            self._url("1::3/1.2.3.5"), [["1.2.3.4"], ["1.2.3.5"], ["1::2"], ["1::3"]]
        )
        self.mock_update.delete.assert_called_with("www.example.com.", "aaaa")
        self.mock_update.add.assert_called_with("www.example.com.", 300, "aaaa", "1::3")
        assert (
            self.data
            == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5\n"
            "UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n"
        )


class TestUpdateByQuery(TestIntegration):
    @staticmethod
    def _url(query_string: str) -> str:
        return (
            "/update-by-query?secret=12345678&record_name=www&zone_name="
            f"example.com&{query_string}"
        )

    def test_unkown_argument(self) -> None:
        self.get("/update-by-query?unknown=unknown")
        assert (
            self.data == 'PARAMETER_ERROR: Unknown query string argument: "unknown"\n'
        )

    def test_ipv4_update(self) -> None:
        side_effect = [["1.2.3.4"], ["1.2.3.5"]]
        self.get(self._url("ipv4=1.2.3.5"), side_effect)

        self.mock_update.delete.assert_has_calls(
            [
                mock.call("www.example.com.", "a"),
                mock.call("www.example.com.", "aaaa"),
            ]
        )
        self.mock_update.add.assert_called_with("www.example.com.", 300, "a", "1.2.3.5")
        assert (
            self.data == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: "
            "1.2.3.5\n"
        )

    def test_ipv6_update(self) -> None:
        side_effect = [["1::2"], ["1::3"]]
        self.get(self._url("ipv6=1::3"), side_effect)
        self.mock_update.delete.assert_called_with("www.example.com.", "aaaa")
        self.mock_update.add.assert_called_with("www.example.com.", 300, "aaaa", "1::3")
        assert (
            self.data == "UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n"
        )

    def test_ipv4_ipv6_update(self) -> None:
        side_effect = [["1.2.3.4"], ["1.2.3.5"], ["1::2"], ["1::3"]]
        self.get(self._url("ipv4=1.2.3.5&ipv6=1::3"), side_effect)
        assert (
            self.data
            == "UPDATED: fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5\n"
            "UPDATED: fqdn: www.example.com. old_ip: 1::2 new_ip: 1::3\n"
        )

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

    def test_ttl(self) -> None:
        side_effect = [["1.2.3.4"], ["1.2.3.5"]]
        self.get(self._url("ipv4=1.2.3.5&ttl=123"), side_effect)
        self.mock_update.add.assert_called_with("www.example.com.", 123, "a", "1.2.3.5")


class TestDeleteByPath(TestIntegration):
    @staticmethod
    def _url(fqdn: str) -> str:
        return f"/delete-by-path/12345678/{fqdn}"

    def test_deletion(self):
        self.get(self._url("www.example.com"))

        self.mock_update.delete.assert_has_calls(
            [
                mock.call("www.example.com.", "a"),
                mock.call("www.example.com.", "aaaa"),
            ]
        )
        self.mock_update.add.assert_not_called()
        assert self.data == 'UPDATED: Deleted "www.example.com.".\n'


class TestCheck(TestIntegration):
    @pytest.mark.skip
    def test_check(self) -> None:
        self.get("/check", TXT(RdataClass.ANY, RdataType.TXT, ("any")))
        assert self.data == 'UPDATED: Deleted "www.example.com.".\n'
