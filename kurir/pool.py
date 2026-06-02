import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

from .interfaces.source import ProxySource
from .interfaces.validator import ProxyValidator
from .interfaces.tracker import HealthTracker
from .interfaces.filter import ProxyFilter


class ProxyPool:
    def __init__(
        self,
        source: ProxySource,
        validator: ProxyValidator,
        tracker: HealthTracker,
        filters: Optional[List[ProxyFilter]] = None,
        workers: int = 50,
        max_valid: Optional[int] = None,
    ) -> None:
        self._source = source
        self._validator = validator
        self._tracker = tracker
        self._filters = filters or []
        self._workers = workers
        self._max_valid = max_valid
        self._proxies: List[str] = []
        self._lock = threading.Lock()

    def refresh(self) -> None:
        raw = self._source.fetch()

        def check(proxy: str):
            return proxy, self._validator.validate(proxy)

        with ThreadPoolExecutor(max_workers=self._workers) as executor:
            results = list(executor.map(check, raw))

        valid = [p for p, ok in results if ok]

        for f in self._filters:
            valid = f.filter(valid)

        with self._lock:
            self._proxies = valid[: self._max_valid] if self._max_valid else valid

    def available(self) -> List[str]:
        with self._lock:
            snapshot = list(self._proxies)
        return self._tracker.get_healthy(snapshot)

    def mark_success(self, proxy: str) -> None:
        self._tracker.record_success(proxy)

    def mark_failed(self, proxy: str) -> None:
        self._tracker.record_failure(proxy)

    def __len__(self) -> int:
        return len(self.available())
