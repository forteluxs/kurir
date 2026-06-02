from unittest.mock import MagicMock
from kurir.pool import ProxyPool


def _make_pool(proxies: list, valid_set: set) -> ProxyPool:
    source = MagicMock()
    source.fetch.return_value = proxies

    validator = MagicMock()
    validator.validate.side_effect = lambda p: p in valid_set

    tracker = MagicMock()
    tracker.get_healthy.side_effect = lambda ps: ps

    return ProxyPool(source, validator, tracker, workers=4)


def test_refresh_keeps_only_valid():
    pool = _make_pool(["a:80", "b:80", "c:80"], {"a:80", "c:80"})
    pool.refresh()
    assert set(pool.available()) == {"a:80", "c:80"}


def test_refresh_respects_max_valid():
    pool = _make_pool(["a:80", "b:80", "c:80"], {"a:80", "b:80", "c:80"})
    pool._max_valid = 2
    pool.refresh()
    assert len(pool.available()) == 2


def test_mark_failed_delegates_to_tracker():
    pool = _make_pool([], set())
    pool.mark_failed("x:80")
    pool._tracker.record_failure.assert_called_once_with("x:80")


def test_mark_success_delegates_to_tracker():
    pool = _make_pool([], set())
    pool.mark_success("x:80")
    pool._tracker.record_success.assert_called_once_with("x:80")


def test_len_reflects_available():
    pool = _make_pool(["a:80", "b:80"], {"a:80", "b:80"})
    pool.refresh()
    assert len(pool) == 2
