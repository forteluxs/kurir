from unittest.mock import MagicMock, patch
import pytest
from kurir.session import KurirSession
from kurir.retry import RetryConfig


def _make_session(proxy: str = "1.1.1.1:80") -> KurirSession:
    pool = MagicMock()
    pool.available.return_value = [proxy]

    strategy = MagicMock()
    strategy.pick.return_value = proxy

    return KurirSession(pool, strategy, RetryConfig(max_attempts=3, timeout=5))


def test_successful_request_marks_success():
    session = _make_session()
    mock_resp = MagicMock(status_code=200)

    with patch("kurir.session.requests.request", return_value=mock_resp):
        resp = session.get("http://example.com")

    assert resp.status_code == 200
    session._pool.mark_success.assert_called_once_with("1.1.1.1:80")
    session._pool.mark_failed.assert_not_called()


def test_failed_request_marks_failed_and_retries():
    session = _make_session()

    with patch("kurir.session.requests.request", side_effect=Exception("timeout")):
        with pytest.raises(Exception, match="timeout"):
            session.get("http://example.com")

    assert session._pool.mark_failed.call_count == 3


def test_no_proxies_raises_runtime_error():
    pool = MagicMock()
    pool.available.return_value = []
    strategy = MagicMock()
    strategy.pick.return_value = None
    session = KurirSession(pool, strategy, RetryConfig())

    with pytest.raises(RuntimeError, match="No healthy proxies"):
        session.get("http://example.com")


def test_all_proxies_exhausted_raises_last_network_error():
    """When proxies run out mid-retry, raise the last real exception, not generic RuntimeError."""
    pool = MagicMock()
    strategy = MagicMock()

    # First attempt has proxy, subsequent attempts have none
    pool.available.side_effect = [["1.1.1.1:80"], [], []]
    strategy.pick.side_effect = ["1.1.1.1:80", None, None]

    session = KurirSession(pool, strategy, RetryConfig(max_attempts=3))

    with patch("kurir.session.requests.request", side_effect=ConnectionError("refused")):
        with pytest.raises(ConnectionError, match="refused"):
            session.get("http://example.com")


def test_rate_limiter_called_before_request():
    session = _make_session()
    rate_limiter = MagicMock()
    session._rate_limiter = rate_limiter
    mock_resp = MagicMock(status_code=200)

    with patch("kurir.session.requests.request", return_value=mock_resp):
        session.get("http://example.com")

    rate_limiter.acquire.assert_called_once()
