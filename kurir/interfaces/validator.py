from abc import ABC, abstractmethod


class ProxyValidator(ABC):
    @abstractmethod
    def validate(self, proxy: str) -> bool:
        """Return True if proxy is reachable and usable."""
        ...
