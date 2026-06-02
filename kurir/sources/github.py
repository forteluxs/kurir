from typing import List

from .url import UrlSource

KNOWN_SOURCES: dict[str, str] = {
    "thesspeedx_http": "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "thesspeedx_socks4": "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "thesspeedx_socks5": "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "clarketm": "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "shiftytr": "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt",
}


class GithubSource(UrlSource):
    def __init__(self, name: str) -> None:
        if name not in KNOWN_SOURCES:
            raise ValueError(
                f"Unknown source '{name}'. Available: {list(KNOWN_SOURCES)}"
            )
        super().__init__(KNOWN_SOURCES[name])

    @staticmethod
    def available_sources() -> List[str]:
        return list(KNOWN_SOURCES)
