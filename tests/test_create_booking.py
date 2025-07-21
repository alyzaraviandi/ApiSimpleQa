import copy
import pytest
import requests

# ---------------------- POSITIVE TESTS ----------------------


def test_create_booking(base_url, logger):
    url = f"{base_url}/booking"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "firstname": "Jim",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2018-01-01",
            "checkout": "2019-01-01"
        },
        "additionalneeds": "Breakfast"
    }

    response = requests.post(url, json=payload, headers=headers)

    logger.info(f"POST {url} - Status Code: {response.status_code}")
    logger.debug(f"Request Payload: {payload}")
    logger.debug(f"Response Body: {response.text}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()

    assert "bookingid" in data, "'bookingid' not in response"
    assert isinstance(data["bookingid"],
                      int), "'bookingid' should be an integer"
    assert "booking" in data, "'booking' not in response"

    booking = data["booking"]
    for field in ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates", "additionalneeds"]:
        assert field in booking, f"Missing field: {field}"

    assert booking["firstname"] == payload["firstname"]
    assert booking["lastname"] == payload["lastname"]
    assert booking["totalprice"] == payload["totalprice"]
    assert booking["depositpaid"] == payload["depositpaid"]
    assert booking["additionalneeds"] == payload["additionalneeds"]
    assert booking["bookingdates"] == payload["bookingdates"]

# ---------------------- NEGATIVE TESTS ----------------------


BASE_PAYLOAD = {
    "firstname": "Jim",
    "lastname": "Brown",
    "totalprice": 111,
    "depositpaid": True,
    "bookingdates": {
        "checkin": "2018-01-01",
        "checkout": "2019-01-01"
    },
    "additionalneeds": "Breakfast"
}


def make_payload_with_invalid_field(field_path, invalid_value):
    """
    Create a deep copy of the base payload and mutate a specific nested field.
    `field_path` should be a list of keys to reach the target (e.g. ["bookingdates", "checkin"])
    """
    payload = copy.deepcopy(BASE_PAYLOAD)
    target = payload
    for key in field_path[:-1]:
        target = target[key]
    target[field_path[-1]] = invalid_value
    return payload


@pytest.mark.parametrize("description,payload,expected_status", [
    pytest.param(
        "Firstname as integer",
        {"firstname": 12345, "lastname": "Smith", "totalprice": 111, "depositpaid": True,
         "bookingdates": {"checkin": "2024-01-01", "checkout": "2024-01-05"}},
        400,
        marks=pytest.mark.xfail(reason="API accepts integer as firstname"),
    ),
    pytest.param(
        "Lastname as boolean",
        {"firstname": "John", "lastname": False, "totalprice": 111, "depositpaid": True,
         "bookingdates": {"checkin": "2024-01-01", "checkout": "2024-01-05"}},
        400,
        marks=pytest.mark.xfail(reason="API accepts boolean as lastname"),
    ),
    pytest.param(
        "Totalprice as string",
        {"firstname": "John", "lastname": "Smith", "totalprice": "one hundred eleven", "depositpaid": True,
         "bookingdates": {"checkin": "2024-01-01", "checkout": "2024-01-05"}},
        400,
        marks=pytest.mark.xfail(
            reason="API accepts string totalprice and sets it as null"),
    ),
    pytest.param(
        "Depositpaid as string",
        {"firstname": "John", "lastname": "Smith", "totalprice": 111, "depositpaid": "yes",
         "bookingdates": {"checkin": "2024-01-01", "checkout": "2024-01-05"}},
        400,
        marks=pytest.mark.xfail(
            reason="API accepts string as boolean for depositpaid"),
    ),
    pytest.param(
        "Checkin date as invalid string",
        {"firstname": "John", "lastname": "Smith", "totalprice": 111, "depositpaid": True,
         "bookingdates": {"checkin": "not-a-date", "checkout": "2024-01-05"}},
        400,
        marks=pytest.mark.xfail(
            reason="API accepts non-date string as checkin"),
    ),
    pytest.param(
        "Checkin date as integer",
        {"firstname": "John", "lastname": "Smith", "totalprice": 111, "depositpaid": True,
         "bookingdates": {"checkin": 123456, "checkout": "2024-01-05"}},
        400,
        marks=pytest.mark.xfail(reason="API accepts integer as checkin date"),
    ),
    pytest.param(
        "Checkout date as boolean",
        {"firstname": "John", "lastname": "Smith", "totalprice": 111, "depositpaid": True,
         "bookingdates": {"checkin": "2024-01-01", "checkout": False}},
        400,
        marks=pytest.mark.xfail(reason="API accepts boolean as checkout date"),
    ),
    pytest.param(
        "Checkin date as null",
        {"firstname": "John", "lastname": "Smith", "totalprice": 111, "depositpaid": True,
         "bookingdates": {"checkin": None, "checkout": "2024-01-05"}},
        400,
        marks=pytest.mark.xfail(reason="API accepts null for checkin"),
    ),
    pytest.param(
        "Checkout date as null",
        {"firstname": "John", "lastname": "Smith", "totalprice": 111, "depositpaid": True,
         "bookingdates": {"checkin": "2024-01-01", "checkout": None}},
        400,
        marks=pytest.mark.xfail(reason="API accepts null for checkout"),
    ),
])
def test_create_booking_with_invalid_data_types(base_url, logger, description, payload, expected_status):
    """Non-happy paths: Booking creation with wrong data types"""
    url = f"{base_url}/booking"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    logger.info(f"Testing: {description}")
    logger.debug(f"POST {url} with payload: {payload}")

    response = requests.post(url, json=payload, headers=headers)
    logger.info(f"Response: {response.status_code} - {response.text}")

    assert response.status_code == expected_status, (
        f"{description}: Expected {expected_status}, got {response.status_code}\n"
        f"Response: {response.text}"
    )
