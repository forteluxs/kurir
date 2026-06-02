# kurir

Composable Python proxy/IP rotator for web scraping and HTTP automation.

## Features

- Rotate exit IP per request using free public proxy lists
- Concurrent proxy validation (ThreadPoolExecutor)
- Geo filtering by country code
- Token bucket rate limiter
- Proxy anonymity checker (elite / anonymous / transparent)
- Thread-safe pool and health tracker
- Swappable strategies: round-robin, random
- All components depend on abstract interfaces — fully composable

## Installation

```bash
git clone https://github.com/forteluxs/kurir.git
cd kurir
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick Start

```python
from kurir import (
    KurirSession, ProxyPool, InMemoryHealthTracker, RetryConfig,
    GithubSource, HttpValidator, RoundRobinStrategy,
)

pool = ProxyPool(
    source=GithubSource("thesspeedx_http"),
    validator=HttpValidator(timeout=5),
    tracker=InMemoryHealthTracker(max_failures=3),
    workers=50,
    max_valid=20,
)

pool.refresh()  # fetch + validate proxies concurrently

session = KurirSession(
    pool=pool,
    strategy=RoundRobinStrategy(),
    retry=RetryConfig(max_attempts=3, timeout=10),
)

resp = session.get("http://httpbin.org/ip")
print(resp.json())  # {"origin": "proxy_ip"}
```

## Components

### Proxy Sources

```python
from kurir import GithubSource, UrlSource, FileSource

# Built-in GitHub sources (auto-updated by maintainers)
GithubSource("thesspeedx_http")    # TheSpeedX/PROXY-List HTTP
GithubSource("thesspeedx_socks4")  # TheSpeedX/PROXY-List SOCKS4
GithubSource("thesspeedx_socks5")  # TheSpeedX/PROXY-List SOCKS5
GithubSource("clarketm")           # clarketm/proxy-list
GithubSource("shiftytr")           # ShiftyTR/Proxy-List

# Custom URL
UrlSource("https://example.com/proxies.txt")

# Local file (one proxy per line, format: ip:port)
FileSource("/path/to/proxies.txt")
```

### Geo Filter

```python
from kurir import GeoFilter

pool = ProxyPool(
    source=GithubSource("thesspeedx_http"),
    validator=HttpValidator(),
    tracker=InMemoryHealthTracker(),
    filters=[GeoFilter({"US", "SG", "DE"})],  # ISO 3166-1 alpha-2
)
```

### Rate Limiter

```python
from kurir import TokenBucketRateLimiter

session = KurirSession(
    pool=pool,
    strategy=RoundRobinStrategy(),
    retry=RetryConfig(),
    rate_limiter=TokenBucketRateLimiter(rate=2, burst=5),  # 2 req/s, burst 5
)
```

### Proxy Checker

```python
from kurir import ProxyChecker

checker = ProxyChecker(workers=50)
results = checker.check_many(["1.2.3.4:8080", "5.6.7.8:3128"])

for info in results:
    print(info.proxy, info.is_valid, info.anonymity, info.response_time_ms)
    # 1.2.3.4:8080 True elite 312.5
    # 5.6.7.8:3128 False None None
```

Anonymity levels:
- `elite` — proxy tidak terdeteksi, IP asli tersembunyi
- `anonymous` — terdeteksi sebagai proxy, IP asli tersembunyi
- `transparent` — IP asli bocor via `X-Forwarded-For`

### Custom Strategy

```python
from kurir.interfaces import RotationStrategy
from typing import List, Optional

class StickyStrategy(RotationStrategy):
    """Always use the first available proxy."""
    def pick(self, proxies: List[str]) -> Optional[str]:
        return proxies[0] if proxies else None
```

## Architecture

```
interfaces/        # Abstract contracts (ProxySource, ProxyValidator,
                   #   RotationStrategy, HealthTracker, ProxyFilter, RateLimiter)
sources/           # UrlSource, FileSource, GithubSource
validators/        # HttpValidator
strategies/        # RoundRobinStrategy, RandomStrategy
filters/           # GeoFilter
rate_limiters/     # TokenBucketRateLimiter
pool.py            # ProxyPool — lifecycle + concurrent validation
health.py          # InMemoryHealthTracker
retry.py           # RetryConfig
session.py         # KurirSession — main entry point
checker.py         # ProxyChecker + ProxyInfo
```

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Notes

- Proxy gratis bersifat publik dan tidak stabil — cocok untuk testing, bukan produksi
- kurir adalah library Python, bukan VPN — hanya request yang dibuat lewat `KurirSession` yang menggunakan proxy
- Untuk HTTPS, sebagian besar proxy gratis tidak mendukung CONNECT tunneling — gunakan `http://` endpoint
