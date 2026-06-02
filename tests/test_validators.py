from unittest.mock import patch, MagicMock
from kurir.validators.http import HttpValidator


def test_returns_true_on_success():
    v = HttpValidator()
    with patch("kurir.validators.http.requests.get", return_value=MagicMock()):
        assert v.validate("1.2.3.4:80") is True


def test_returns_false_on_connection_error():
    v = HttpValidator()
    with patch("kurir.validators.http.requests.get", side_effect=Exception("timeout")):
        assert v.validate("1.2.3.4:80") is False
