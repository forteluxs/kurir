from unittest.mock import patch, MagicMock
from kurir.filters.geo import GeoFilter


def _mock_geo(responses: dict):
    """responses: {ip: country_code}"""
    def fake_get(url, timeout):
        ip = url.split("/json/")[1].split("?")[0]
        code = responses.get(ip, "")
        m = MagicMock()
        m.json.return_value = {"status": "success", "countryCode": code} if code else {"status": "fail"}
        return m
    return fake_get


def test_keeps_proxies_in_allowed_countries():
    f = GeoFilter({"US", "DE"}, workers=2)
    proxies = ["1.1.1.1:80", "2.2.2.2:80", "3.3.3.3:80"]

    with patch("kurir.filters.geo.requests.get", side_effect=_mock_geo({
        "1.1.1.1": "US",
        "2.2.2.2": "FR",
        "3.3.3.3": "DE",
    })):
        result = f.filter(proxies)

    assert set(result) == {"1.1.1.1:80", "3.3.3.3:80"}


def test_drops_proxies_with_failed_geo_lookup():
    f = GeoFilter({"US"}, workers=2)

    with patch("kurir.filters.geo.requests.get", side_effect=Exception("network error")):
        result = f.filter(["1.1.1.1:80"])

    assert result == []


def test_country_codes_are_case_insensitive():
    f = GeoFilter({"us"}, workers=2)

    with patch("kurir.filters.geo.requests.get", side_effect=_mock_geo({"1.1.1.1": "US"})):
        result = f.filter(["1.1.1.1:80"])

    assert result == ["1.1.1.1:80"]
