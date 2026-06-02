from abc import ABC, abstractmethod
from typing import List


class HealthTracker(ABC):
    @abstractmethod
    def record_success(self, proxy: str) -> None: ...

    @abstractmethod
    def record_failure(self, proxy: str) -> None: ...

    @abstractmethod
    def is_healthy(self, proxy: str) -> bool: ...

    @abstractmethod
    def get_healthy(self, proxies: List[str]) -> List[str]: ...
