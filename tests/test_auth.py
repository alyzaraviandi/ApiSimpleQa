import requests
import pytest

AUTH_URL = "https://restful-booker.herokuapp.com/auth"
HEADERS = {
    "Content-Type": "application/json"
}

# ---------------------- POSITIVE TESTS ----------------------


def test_auth_token_success(logger):
    """Happy path: Valid credentials return token"""
    payload = {
        "username": "admin",
        "password": "password123"
    }

    logger.info("Sending POST request to /auth with valid credentials")
    response = requests.post(AUTH_URL, json=payload, headers=HEADERS)
    logger.debug(f"Auth response: {response.status_code} - {response.text}")

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert isinstance(data["token"], str) and len(data["token"]) > 0
    logger.info("Auth token successfully retrieved")

# ---------------------- NEGATIVE TESTS ----------------------


@pytest.mark.parametrize("description,payload,expected_status", [
    pytest.param(
        "invalid username", {"username": "wrong",
                             "password": "password123"}, 401,
        marks=pytest.mark.xfail(
            reason="API returns 200 with 'Bad credentials' instead of 401")
    ),
    pytest.param(
        "invalid password", {"username": "admin", "password": "wrong"}, 401,
        marks=pytest.mark.xfail(
            reason="API returns 200 with 'Bad credentials' instead of 401")
    ),
    pytest.param(
        "invalid both", {"username": "wrong", "password": "wrong"}, 401,
        marks=pytest.mark.xfail(
            reason="API returns 200 with 'Bad credentials' instead of 401")
    ),
    pytest.param(
        "missing username", {"password": "password123"}, 400,
        marks=pytest.mark.xfail(
            reason="API does not validate missing username; still returns 200")
    ),
    pytest.param(
        "missing password", {"username": "admin"}, 400,
        marks=pytest.mark.xfail(
            reason="API does not validate missing password; still returns 200")
    ),
    pytest.param(
        "missing both", {}, 400,
        marks=pytest.mark.xfail(
            reason="API accepts empty auth payload; still returns 200")
    ),
])
def test_auth_invalid_credentials_or_missing_fields(description, payload, expected_status, logger):
    """Non-happy paths: Invalid credentials or missing fields"""
    logger.info(f"Testing auth with {description}: {payload}")
    response = requests.post(AUTH_URL, json=payload, headers=HEADERS)
    logger.debug(f"Response: {response.status_code} - {response.text}")

    assert response.status_code == expected_status, (
        f"{description}: Expected {expected_status}, got {response.status_code}"
    )

    data = response.json()
    if expected_status == 401:
        assert data.get("reason", "").lower(
        ) == "bad credentials", f"{description}: Unexpected reason"
        assert "token" not in data, f"{description}: Token should not be returned"
    elif expected_status == 400:
        # optional: customize this if the API returns specific error message for missing fields
        assert "reason" in data or "error" in data, f"{description}: Error message expected"

def test_auth_non_json_payload(logger):
    """Non-happy path: Sending non-JSON payload"""
    logger.info("Testing auth with non-JSON payload")
    response = requests.post(
        AUTH_URL, data="username=admin&password=password123", headers=HEADERS)
    logger.debug(
        f"Non-JSON response: {response.status_code} - {response.text}")

    assert response.status_code in [
        400, 500], "Expected 400/500 for malformed payload"
