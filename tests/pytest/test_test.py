from custom_test import test_network, test_property  # noqa: E402


def test_test_network():
    host = "test.com"
    address = "10.0.0.1"
    r = {"host": host, "address": address}
    assert not test_network(r)
    assert not test_network(r, "10.0.0.0/24")
    assert not test_network(r, "10.1.0.0/24")
    assert test_network(r, "10.0.0.0/24", "address") == r


def test_test_property():
    host = "test.com"
    address = "10.0.0.1"
    r = {"host": host, "address": address}
    assert not test_property(r, ".*", "none")
    assert not test_property(r, "nomatch", "host")
    assert test_property(r, ".*.com", "host") == r
