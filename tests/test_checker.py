from unittest.mock import patch, MagicMock
from kurir.checker import ProxyChecker, ProxyInfo


def _mock_response(headers: dict):
    m = MagicMock()
    m.json.return_value = {"headers": headers}
    return m


def test_valid_proxy_returns_info():
    checker = ProxyChecker()
    with patch("kurir.checker.requests.get", return_value=_mock_response({})):
        info = checker.check("1.2.3.4:80")

    assert info.is_valid is True
    assert info.proxy == "1.2.3.4:80"
    assert info.response_time_ms is not None


def test_unreachable_proxy_returns_invalid():
    checker = ProxyChecker()
    with patch("kurir.checker.requests.get", side_effect=Exception("timeout")):
        info = checker.check("1.2.3.4:80")

    assert info.is_valid is False
    assert info.anonymity is None


def test_detects_elite_anonymity():
    checker = ProxyChecker()
    with patch("kurir.checker.requests.get", return_value=_mock_response({})):
        info = checker.check("1.2.3.4:80")
    assert info.anonymity == "elite"


def test_detects_transparent_proxy():
    checker = ProxyChecker()
    headers = {"X-Forwarded-For": "real-ip"}
    with patch("kurir.checker.requests.get", return_value=_mock_response(headers)):
        info = checker.check("1.2.3.4:80")
    assert info.anonymity == "transparent"


def test_detects_anonymous_proxy():
    checker = ProxyChecker()
    headers = {"Via": "1.1 proxy"}
    with patch("kurir.checker.requests.get", return_value=_mock_response(headers)):
        info = checker.check("1.2.3.4:80")
    assert info.anonymity == "anonymous"


def test_check_many_returns_list_of_proxy_info():
    checker = ProxyChecker(workers=2)
    proxies = ["1.1.1.1:80", "2.2.2.2:80"]
    with patch("kurir.checker.requests.get", return_value=_mock_response({})):
        results = checker.check_many(proxies)

    assert len(results) == 2
    assert all(isinstance(r, ProxyInfo) for r in results)
