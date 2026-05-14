from pnkln_stack_core import ping


def test_ping():
    assert ping() == "pong"
