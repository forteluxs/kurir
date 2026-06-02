from abc import ABC, abstractmethod
from typing import List, Optional


class RotationStrategy(ABC):
    @abstractmethod
    def pick(self, proxies: List[str]) -> Optional[str]:
        """Select the next proxy from the available pool."""
        ...
