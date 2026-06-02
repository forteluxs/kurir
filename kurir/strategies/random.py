import random
from typing import List, Optional

from ..interfaces.strategy import RotationStrategy


class RandomStrategy(RotationStrategy):
    def pick(self, proxies: List[str]) -> Optional[str]:
        if not proxies:
            return None
        return random.choice(proxies)
