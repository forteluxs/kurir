from concurrent.futures import ThreadPoolExecutor
from typing import List, Set

import requests

from ..interfaces.filter import ProxyFilter

_GEO_API = "http://ip-api.com/json/{ip}?fields=countryCode,status"


class GeoFilter(ProxyFilter):
    """Keep only proxies whose exit IP resolves to an allowed country."""

    def __init__(self, allowed_countries: Set[str], workers: int = 20) -> None:
        self._allowed = {c.upper() for c in allowed_countries}
        self._workers = workers

    def _country_code(self, proxy: str) -> tuple[str, str]:
        ip = proxy.split(":")[0]
        try:
            resp = requests.get(_GEO_API.format(ip=ip), timeout=5)
            data = resp.json()
            if data.get("status") == "success":
                return proxy, data.get("countryCode", "")
        except Exception:
            pass
        return proxy, ""

    def filter(self, proxies: List[str]) -> List[str]:
        with ThreadPoolExecutor(max_workers=self._workers) as executor:
            results = list(executor.map(self._country_code, proxies))
        return [p for p, code in results if code in self._allowed]
