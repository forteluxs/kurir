from typing import List

import requests

from ..interfaces.source import ProxySource


class UrlSource(ProxySource):
    def __init__(self, url: str, timeout: int = 10) -> None:
        self._url = url
        self._timeout = timeout

    def fetch(self) -> List[str]:
        resp = requests.get(self._url, timeout=self._timeout)
        resp.raise_for_status()
        text = resp.content.decode("utf-8", errors="ignore")
        return [line.strip() for line in text.splitlines() if line.strip()]
