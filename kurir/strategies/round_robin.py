import threading
from typing import List, Optional

from ..interfaces.strategy import RotationStrategy


class RoundRobinStrategy(RotationStrategy):
    def __init__(self) -> None:
        self._index = 0
        self._lock = threading.Lock()

    def pick(self, proxies: List[str]) -> Optional[str]:
        if not proxies:
            return None
        with self._lock:
            proxy = proxies[self._index % len(proxies)]
            self._index += 1
        return proxy
