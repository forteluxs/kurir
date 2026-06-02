from abc import ABC, abstractmethod


class RateLimiter(ABC):
    @abstractmethod
    def acquire(self) -> None:
        """Block until a request slot is available."""
        ...
