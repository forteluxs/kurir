from abc import ABC, abstractmethod
from typing import List


class ProxyFilter(ABC):
    @abstractmethod
    def filter(self, proxies: List[str]) -> List[str]:
        """Return subset of proxies that pass this filter."""
        ...
