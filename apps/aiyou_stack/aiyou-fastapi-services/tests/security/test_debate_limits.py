from fastapi.testclient import TestClient

from app.main_ecosystem import app

client = TestClient(app)


def test_debate_limits_valid():
    response = client.post("/debate", params={"question": "test", "num_agents": 3, "max_rounds": 3})
    # Since we don't have the full environment set up (missing models probably), it might fail with 500 or similar inside the logic,
    # but validation should pass. So we check that it is NOT 422.
    # Actually, the logic might fail if models aren't loaded.
    # However, for this specific vulnerability check, we only care that validation *passes* or *fails*.
    # If validation passes, it might hit downstream errors.
    # Let's check that we don't get 422 for valid input.
    assert response.status_code != 422


def test_debate_limits_invalid_agents():
    response = client.post(
        "/debate",
        params={"question": "test", "num_agents": 100, "max_rounds": 3},
    )
    assert response.status_code == 422
    assert (
        "Input should be less than or equal to 10" in response.text
        or "less than or equal to 10" in str(response.json())
    )


def test_debate_limits_invalid_rounds():
    response = client.post(
        "/debate",
        params={"question": "test", "num_agents": 3, "max_rounds": 100},
    )
    assert response.status_code == 422
    assert (
        "Input should be less than or equal to 20" in response.text
        or "less than or equal to 20" in str(response.json())
    )
