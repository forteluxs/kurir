import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Literal, Optional

import requests

_TEST_URL = "http://httpbin.org/get"

Anonymity = Literal["elite", "anonymous", "transparent"]


@dataclass
class ProxyInfo:
    proxy: str
    is_valid: bool
    anonymity: Optional[Anonymity] = None
    response_time_ms: Optional[float] = None


class ProxyChecker:
    """Checks connectivity and anonymity level of proxies concurrently."""

    def __init__(
        self,
        test_url: str = _TEST_URL,
        timeout: int = 10,
        workers: int = 50,
    ) -> None:
        self._test_url = test_url
        self._timeout = timeout
        self._workers = workers

    def check(self, proxy: str) -> ProxyInfo:
        start = time.monotonic()
        try:
            resp = requests.get(
                self._test_url,
                proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                timeout=self._timeout,
            )
            elapsed_ms = round((time.monotonic() - start) * 1000, 2)
            headers = {k.lower(): v for k, v in resp.json().get("headers", {}).items()}
            return ProxyInfo(
                proxy=proxy,
                is_valid=True,
                anonymity=self._detect_anonymity(headers),
                response_time_ms=elapsed_ms,
            )
        except Exception:
            return ProxyInfo(proxy=proxy, is_valid=False)

    def check_many(self, proxies: List[str]) -> List[ProxyInfo]:
        with ThreadPoolExecutor(max_workers=self._workers) as executor:
            return list(executor.map(self.check, proxies))

    @staticmethod
    def _detect_anonymity(headers: dict) -> Anonymity:
        if "x-forwarded-for" in headers or "x-real-ip" in headers:
            return "transparent"
        if "via" in headers or "proxy-connection" in headers:
            return "anonymous"
        return "elite"
