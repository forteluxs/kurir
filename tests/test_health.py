from kurir.health import InMemoryHealthTracker


def test_healthy_by_default():
    t = InMemoryHealthTracker()
    assert t.is_healthy("1.1.1.1:80")


def test_unhealthy_after_max_failures():
    t = InMemoryHealthTracker(max_failures=2)
    t.record_failure("1.1.1.1:80")
    assert t.is_healthy("1.1.1.1:80")
    t.record_failure("1.1.1.1:80")
    assert not t.is_healthy("1.1.1.1:80")


def test_success_resets_failures():
    t = InMemoryHealthTracker(max_failures=2)
    t.record_failure("1.1.1.1:80")
    t.record_success("1.1.1.1:80")
    t.record_failure("1.1.1.1:80")
    assert t.is_healthy("1.1.1.1:80")


def test_get_healthy_filters():
    t = InMemoryHealthTracker(max_failures=1)
    t.record_failure("bad:80")
    result = t.get_healthy(["good:80", "bad:80"])
    assert result == ["good:80"]
