from abc import ABC, abstractmethod
from typing import List


class ProxySource(ABC):
    @abstractmethod
    def fetch(self) -> List[str]:
        """Return list of proxies as 'host:port' strings."""
        ...
