from typing import Any, Optional

import requests

from .pool import ProxyPool
from .interfaces.strategy import RotationStrategy
from .interfaces.rate_limiter import RateLimiter
from .retry import RetryConfig


class KurirSession:
    def __init__(
        self,
        pool: ProxyPool,
        strategy: RotationStrategy,
        retry: RetryConfig,
        rate_limiter: Optional[RateLimiter] = None,
    ) -> None:
        self._pool = pool
        self._strategy = strategy
        self._retry = retry
        self._rate_limiter = rate_limiter

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        return self._request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        return self._request("POST", url, **kwargs)

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        return self._request(method, url, **kwargs)

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        if self._rate_limiter:
            self._rate_limiter.acquire()

        last_exc: Optional[Exception] = None

        for _ in range(self._retry.max_attempts):
            # Fetch fresh list each attempt so health changes are reflected
            proxy = self._strategy.pick(self._pool.available())
            if proxy is None:
                break

            try:
                resp = requests.request(
                    method,
                    url,
                    proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                    timeout=self._retry.timeout,
                    **kwargs,
                )
                self._pool.mark_success(proxy)
                return resp
            except Exception as exc:
                self._pool.mark_failed(proxy)
                last_exc = exc

        if last_exc:
            raise last_exc
        raise RuntimeError("No healthy proxies available")
