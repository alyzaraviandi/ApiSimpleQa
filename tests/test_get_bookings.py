import requests
import pytest

BOOKING_ENDPOINT = "/booking"

# ---------------------- POSITIVE TESTS ----------------------

def test_get_all_booking_ids_success(base_url, logger):
    url = f"{base_url}{BOOKING_ENDPOINT}"
    response = requests.get(url)

    logger.info(f"GET {url} - Status Code: {response.status_code}")
    logger.debug(f"Response Body: {response.text}")

    assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"
    data = response.json()
    assert isinstance(data, list), "Expected response to be a list"

    if data:
        assert "bookingid" in data[0], "Missing 'bookingid' in response item"
        assert isinstance(data[0]["bookingid"], int), "'bookingid' should be an integer"


def test_get_booking_by_firstname_success(base_url, logger):
    url = f"{base_url}{BOOKING_ENDPOINT}"
    params = {"firstname": "Jim"}
    response = requests.get(url, params=params)

    logger.info(f"GET {url} with params {params} - Status Code: {response.status_code}")
    logger.debug(f"Response Body: {response.text}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_booking_by_date_range_success(base_url, logger):
    url = f"{base_url}{BOOKING_ENDPOINT}"
    params = {"checkin": "2024-01-01", "checkout": "2024-01-05"}
    response = requests.get(url, params=params)

    logger.info(f"GET {url} with params {params} - Status Code: {response.status_code}")
    logger.debug(f"Response Body: {response.text}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------- NEGATIVE TESTS ----------------------

@pytest.mark.parametrize("description,params,expected_status", [
    pytest.param(
        "invalid query key: first_name",
        {"first_name": "Jim"},
        400,
        marks=pytest.mark.xfail(reason="API does not validate unknown query param keys")
    ),
])
def test_get_booking_with_query_params_validation(base_url, logger, description, params, expected_status):
    url = f"{base_url}{BOOKING_ENDPOINT}"
    response = requests.get(url, params=params)

    logger.info(f"{description} - GET {url} with {params} - Status: {response.status_code}")
    logger.debug(f"Response Body: {response.text}")

    assert response.status_code == expected_status


@pytest.mark.parametrize("description,params", [
    pytest.param(
        "wrong checkin format", {"checkin": "01-01-2024", "checkout": "2024-01-05"},
        marks=pytest.mark.xfail(reason="API accepts non-ISO date format instead of returning 400")
    ),
    pytest.param(
        "invalid checkout string", {"checkin": "2024-01-01", "checkout": "not-a-date"},
        marks=pytest.mark.xfail(reason="API accepts invalid date string instead of returning 400")
    ),
    pytest.param(
        "invalid checkin month", {"checkin": "2024-13-01", "checkout": "2024-01-05"},
        marks=pytest.mark.xfail(reason="API returns 500 instead of 400 for invalid month")
    ),
])
def test_get_booking_invalid_date_format(base_url, description, params, logger):
    url = f"{base_url}/booking"
    response = requests.get(url, params=params)

    logger.info(f"{description} → GET {url} with params {params} - Status Code: {response.status_code}")
    logger.debug(f"Response Body: {response.text}")

    assert response.status_code == 400, f"{description} → Expected 400, got {response.status_code}"

