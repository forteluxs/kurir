from kurir import (
    KurirSession,
    ProxyPool,
    InMemoryHealthTracker,
    RetryConfig,
    GithubSource,
    HttpValidator,
    RoundRobinStrategy,
)

source = GithubSource("thesspeedx_http")
validator = HttpValidator(timeout=5)
tracker = InMemoryHealthTracker(max_failures=3)

pool = ProxyPool(source, validator, tracker, workers=50, max_valid=20)

print("Fetching & validating proxies...")
pool.refresh()
print(f"Pool ready: {len(pool)} healthy proxies")

session = KurirSession(
    pool=pool,
    strategy=RoundRobinStrategy(),
    retry=RetryConfig(max_attempts=3, timeout=10),
)

for i in range(5):
    try:
        resp = session.get("http://httpbin.org/ip")
        print(f"[{i+1}] IP: {resp.json().get('origin')}")
    except Exception as e:
        print(f"[{i+1}] Failed: {e}")
