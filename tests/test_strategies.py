from kurir.strategies.round_robin import RoundRobinStrategy
from kurir.strategies.random import RandomStrategy


def test_round_robin_cycles():
    s = RoundRobinStrategy()
    proxies = ["a", "b", "c"]
    assert s.pick(proxies) == "a"
    assert s.pick(proxies) == "b"
    assert s.pick(proxies) == "c"
    assert s.pick(proxies) == "a"


def test_round_robin_empty_returns_none():
    assert RoundRobinStrategy().pick([]) is None


def test_random_picks_from_list():
    s = RandomStrategy()
    proxies = ["a", "b", "c"]
    assert s.pick(proxies) in proxies


def test_random_empty_returns_none():
    assert RandomStrategy().pick([]) is None
