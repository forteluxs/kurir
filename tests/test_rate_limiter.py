import time
import pytest
from kurir.rate_limiters.token_bucket import TokenBucketRateLimiter


def test_acquire_does_not_block_within_burst():
    limiter = TokenBucketRateLimiter(rate=10, burst=3)
    start = time.monotonic()
    limiter.acquire()
    limiter.acquire()
    limiter.acquire()
    elapsed = time.monotonic() - start
    assert elapsed < 0.1


def test_acquire_throttles_beyond_burst():
    limiter = TokenBucketRateLimiter(rate=5, burst=1)
    limiter.acquire()  # consume burst token

    start = time.monotonic()
    limiter.acquire()  # should wait ~0.2s
    elapsed = time.monotonic() - start

    assert elapsed >= 0.15


def test_rate_limiter_respects_interface():
    from kurir.interfaces.rate_limiter import RateLimiter
    assert isinstance(TokenBucketRateLimiter(rate=100, burst=10), RateLimiter)


def test_zero_rate_raises():
    with pytest.raises(ValueError, match="rate must be positive"):
        TokenBucketRateLimiter(rate=0)


def test_negative_rate_raises():
    with pytest.raises(ValueError, match="rate must be positive"):
        TokenBucketRateLimiter(rate=-1)


def test_zero_burst_raises():
    with pytest.raises(ValueError, match="burst must be >= 1"):
        TokenBucketRateLimiter(rate=1, burst=0)
