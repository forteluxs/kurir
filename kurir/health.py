import threading
from dataclasses import dataclass
from typing import Dict, List

from .interfaces.tracker import HealthTracker


@dataclass
class _ProxyStats:
    failures: int = 0
    successes: int = 0


class InMemoryHealthTracker(HealthTracker):
    def __init__(self, max_failures: int = 3) -> None:
        self._max_failures = max_failures
        self._stats: Dict[str, _ProxyStats] = {}
        self._lock = threading.Lock()

    def _stats_for(self, proxy: str) -> _ProxyStats:
        # setdefault is atomic under the GIL; lock is still held by caller
        return self._stats.setdefault(proxy, _ProxyStats())

    def record_success(self, proxy: str) -> None:
        with self._lock:
            stats = self._stats_for(proxy)
            stats.successes += 1
            stats.failures = 0

    def record_failure(self, proxy: str) -> None:
        with self._lock:
            self._stats_for(proxy).failures += 1

    def is_healthy(self, proxy: str) -> bool:
        with self._lock:
            return self._stats_for(proxy).failures < self._max_failures

    def get_healthy(self, proxies: List[str]) -> List[str]:
        with self._lock:
            return [
                p for p in proxies
                if self._stats.get(p, _ProxyStats()).failures < self._max_failures
            ]
