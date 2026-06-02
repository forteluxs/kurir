from pathlib import Path
from typing import List, Union

from ..interfaces.source import ProxySource


class FileSource(ProxySource):
    def __init__(self, path: Union[str, Path]) -> None:
        self._path = Path(path)

    def fetch(self) -> List[str]:
        return [
            line.strip()
            for line in self._path.read_text().splitlines()
            if line.strip()
        ]
