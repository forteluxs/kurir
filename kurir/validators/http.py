import requests

from ..interfaces.validator import ProxyValidator

_TEST_URL = "http://httpbin.org/ip"


class HttpValidator(ProxyValidator):
    def __init__(self, test_url: str = _TEST_URL, timeout: int = 5) -> None:
        self._test_url = test_url
        self._timeout = timeout

    def validate(self, proxy: str) -> bool:
        try:
            resp = requests.get(
                self._test_url,
                proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                timeout=self._timeout,
            )
            resp.json()
            return True
        except Exception:
            return False
