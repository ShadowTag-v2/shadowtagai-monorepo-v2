from ShadowTag-v2_core import ping


def test_ping():
    assert ping() == "pong"
