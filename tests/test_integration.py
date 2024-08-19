from tests.conftest import TestClient


class TestUpdateByPath:
    @staticmethod
    def url(path: str) -> str:
        return f"/update-by-path/12345678/test.dyndns1.dev/{path}"

    def test_ipv4_update(self, client: TestClient) -> None:
        client.add_record("test", "A", "1.2.3.4")
        assert (
            client.get(self.url("1.2.3.5"))
            == "UPDATED: test.dyndns1.dev. A 1.2.3.4 -> 1.2.3.5\n"
            + "UNCHANGED: test.dyndns1.dev. AAAA None\n"
        )
        assert client.read_record("test", "A") == "1.2.3.5"

    def test_ipv6_update(self, client: TestClient) -> None:
        client.add_record("test", "AAAA", "1::2")
        assert (
            client.get(self.url("1::3"))
            == "UNCHANGED: test.dyndns1.dev. A None\n"
            + "UPDATED: test.dyndns1.dev. AAAA 1::2 -> 1::3\n"
        )
        assert client.read_record("test", "AAAA") == "1::3"

    def test_ipv4_ipv6_update(self, client: TestClient) -> None:
        client.add_record("test", "A", "1.2.3.4")
        client.add_record("test", "AAAA", "1::2")
        assert (
            client.get(self.url("1.2.3.5/1::3"))
            == "UPDATED: test.dyndns1.dev. A 1.2.3.4 -> 1.2.3.5\n"
            + "UPDATED: test.dyndns1.dev. AAAA 1::2 -> 1::3\n"
        )
        assert client.read_record("test", "A") == "1.2.3.5"
        assert client.read_record("test", "AAAA") == "1::3"

    def test_wrong_secret(self, client: TestClient) -> None:
        response = client.get_response(
            "/update-by-path/wrong-secret/test.example.com/1.2.3.4"
        )
        assert response.status_code == 456
        assert (
            response.data.decode()
            == "PARAMETER_ERROR: You specified a wrong secret key.\n"
        )

        assert client.read_record("test", "A") is None
        assert client.read_record("test", "AAAA") is None

    def test_wrong_fqdn(self, client: TestClient) -> None:
        response = client.get_response(
            "/update-by-path/12345678/test.wrong-domain.de/1.2.3.4"
        )
        assert response.status_code == 453
        assert (
            response.data.decode()
            == "DNS_NAME_ERROR: The fully qualified domain name 'test.wrong-domain.de.' could not be split into a record and a zone name.\n"
        )

    def test_wrong_ip(self, client: TestClient) -> None:
        response = client.get_response(self.url("1.2.3"))
        assert response.status_code == 454
        assert (
            response.data.decode() == "IP_ADDRESS_ERROR: Invalid IP address '1.2.3'.\n"
        )


class TestUpdateByQuery:
    """Test the path ``update-by-query`` of the Flask web app."""

    @staticmethod
    def url(query_string: str) -> str:
        return (
            "/update-by-query?secret=12345678&record_name=test&zone_name="
            f"dyndns1.dev&{query_string}"
        )

    def test_unkown_argument(self, client: TestClient) -> None:
        response = client.get_response(self.url("unknown=unknown"))
        assert response.status_code == 456
        assert (
            response.data.decode()
            == "PARAMETER_ERROR: extra_forbidden: Extra inputs are not permitted (unknown).\n"
        )

    def test_ipv4_update(self, client: TestClient) -> None:
        client.add_record("test", "A", "1.2.3.4")
        assert (
            client.get(self.url("ipv4=1.2.3.5"))
            == "UPDATED: test.dyndns1.dev. A 1.2.3.4 -> 1.2.3.5\n"
            + "UNCHANGED: test.dyndns1.dev. AAAA None\n"
        )
        assert client.read_record("test", "A") == "1.2.3.5"

    def test_ipv6_update(self, client: TestClient) -> None:
        client.add_record("test", "AAAA", "1::2")
        assert (
            client.get(self.url("ipv6=1::3"))
            == "UNCHANGED: test.dyndns1.dev. A None\n"
            + "UPDATED: test.dyndns1.dev. AAAA 1::2 -> 1::3\n"
        )
        assert client.read_record("test", "AAAA") == "1::3"

    def test_ipv4_ipv6_update(self, client: TestClient) -> None:
        client.add_record("test", "A", "1.2.3.4")
        client.add_record("test", "AAAA", "1::2")
        assert (
            client.get(self.url("ipv4=1.2.3.5&ipv6=1::3"))
            == "UPDATED: test.dyndns1.dev. A 1.2.3.4 -> 1.2.3.5\n"
            + "UPDATED: test.dyndns1.dev. AAAA 1::2 -> 1::3\n"
        )
        assert client.read_record("test", "A") == "1.2.3.5"
        assert client.read_record("test", "AAAA") == "1::3"

    def test_ip_1_ip_2_update(self, client: TestClient) -> None:
        client.add_record("test", "A", "1.2.3.4")
        client.add_record("test", "AAAA", "1::2")
        assert (
            client.get(self.url("ip_1=1.2.3.5&ip_2=1::3"))
            == "UPDATED: test.dyndns1.dev. A 1.2.3.4 -> 1.2.3.5\n"
            + "UPDATED: test.dyndns1.dev. AAAA 1::2 -> 1::3\n"
        )
        assert client.read_record("test", "A") == "1.2.3.5"
        assert client.read_record("test", "AAAA") == "1::3"

    def test_invalid_ipv4(self, client: TestClient) -> None:
        assert (
            client.get(self.url("ipv4=1.2.3.4.5"))
            == "IP_ADDRESS_ERROR: Invalid IP address '1.2.3.4.5'.\n"
        )

    def test_ttl(self, client: TestClient) -> None:
        client.delete_record("test", "A")
        client.get(self.url("ipv4=1.2.3.5&ttl=123"))
        rrset = client.read_resource_record_set("test", "A")
        assert rrset
        assert rrset.ttl == 123


def test_delete_by_path(client: TestClient) -> None:
    client.add_record("test", "A", "1.2.3.4")
    client.add_record("test", "AAAA", "1::2")
    assert (
        client.get("/delete-by-path/12345678/test.dyndns1.dev.")
        == "UPDATED: The A and AAAA records of the domain name 'test.dyndns1.dev.' were deleted.\n"
    )
    assert client.read_record("test", "A") is None
    assert client.read_record("test", "AAAA") is None


class TestMultiplePaths:
    def test_home(self, client: TestClient) -> None:
        assert client.get("/") == "dyndns\n"

    def test_check(self, client: TestClient) -> None:
        content = client.get("/check")
        assert content
        assert "could be updated on the zone 'dyndns1.dev.'" in content
        assert "could be updated on the zone 'dyndns2.dev.'" in content
