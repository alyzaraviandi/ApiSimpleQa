import requests
import pytest

# -------------------------- POSITIVE TESTS --------------------------
@pytest.mark.usefixtures("base_url", "logger", "headers_with_token")
def test_update_booking(base_url, logger, headers_with_token):
    # Step 1: Create a booking to update
    create_url = f"{base_url}/booking"
    create_payload = {
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
    create_response = requests.post(create_url, json=create_payload)
    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    # Step 2: Update the booking
    update_url = f"{base_url}/booking/{booking_id}"
    update_payload = {
        "firstname": "James",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2018-01-01",
            "checkout": "2019-01-01"
        },
        "additionalneeds": "Breakfast"
    }

    response = requests.put(update_url, json=update_payload, headers=headers_with_token)

    logger.info(f"PUT {update_url} - Status Code: {response.status_code}")
    logger.debug(f"Update Payload: {update_payload}")
    logger.debug(f"Response Body: {response.text}")

    assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"
    updated = response.json()

    # Validate updated fields
    assert updated["firstname"] == update_payload["firstname"]
    assert updated["lastname"] == update_payload["lastname"]
    assert updated["totalprice"] == update_payload["totalprice"]
    assert updated["depositpaid"] == update_payload["depositpaid"]
    assert updated["additionalneeds"] == update_payload["additionalneeds"]
    assert updated["bookingdates"] == update_payload["bookingdates"]

# -------------------------- NEGATIVE TESTS --------------------------

def test_update_booking_without_token(base_url, logger):
    payload = {
        "firstname": "Unauth",
        "lastname": "User",
        "totalprice": 100,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2024-01-01",
            "checkout": "2024-01-05"
        },
        "additionalneeds": "None"
    }
    # Create a booking
    response = requests.post(f"{base_url}/booking", json=payload)
    booking_id = response.json()["bookingid"]

    # Attempt update without auth
    update_payload = payload.copy()
    update_payload["firstname"] = "Unauthorized"

    update_response = requests.put(
        f"{base_url}/booking/{booking_id}",
        json=update_payload,
        headers={"Content-Type": "application/json"}
    )

    logger.info(f"PUT without token - Status: {update_response.status_code}")
    assert update_response.status_code == 403


def test_update_booking_with_invalid_token(base_url, logger):
    payload = {
        "firstname": "Invalid",
        "lastname": "Token",
        "totalprice": 222,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2024-02-01",
            "checkout": "2024-02-07"
        },
        "additionalneeds": "WiFi"
    }
    response = requests.post(f"{base_url}/booking", json=payload)
    booking_id = response.json()["bookingid"]

    invalid_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": "token=faketoken123"
    }

    update_response = requests.put(
        f"{base_url}/booking/{booking_id}",
        headers=invalid_headers,
        json=payload
    )

    logger.info(f"PUT with invalid token - Status: {update_response.status_code}")
    assert update_response.status_code == 403


def test_update_nonexistent_booking(base_url, headers_with_token, logger):
    fake_id = 999999
    update_payload = {
        "firstname": "Ghost",
        "lastname": "Booking",
        "totalprice": 999,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2025-01-01",
            "checkout": "2025-01-10"
        },
        "additionalneeds": "None"
    }

    response = requests.put(
        f"{base_url}/booking/{fake_id}",
        json=update_payload,
        headers=headers_with_token
    )

    logger.info(f"PUT to nonexistent booking - Status: {response.status_code}")
    assert response.status_code in [404, 405]


@pytest.mark.parametrize("description,invalid_field_payload,expected_status", [
    pytest.param(
        "Firstname as integer", {"firstname": 12345}, 400,
        marks=pytest.mark.xfail(reason="API accepts integer as firstname"),
    ),
    pytest.param(
        "Lastname as boolean", {"lastname": False}, 400,
        marks=pytest.mark.xfail(reason="API accepts boolean as lastname"),
    ),
    pytest.param(
        "Totalprice as string", {"totalprice": "one hundred"}, 400,
        marks=pytest.mark.xfail(reason="API accepts totalprice as string and sets to null"),
    ),
    pytest.param(
        "Depositpaid as string", {"depositpaid": "true"}, 400,
        marks=pytest.mark.xfail(reason="API accepts depositpaid as string"),
    ),
    pytest.param(
        "Checkin as integer", {"bookingdates": {"checkin": 20230701}}, 400,
        marks=pytest.mark.xfail(reason="API accepts checkin as integer"),
    ),
    pytest.param(
        "Checkout as boolean", {"bookingdates": {"checkout": True}}, 400,
        marks=pytest.mark.xfail(reason="API accepts checkout as boolean"),
    ),
])
def test_update_booking_with_invalid_data_types(base_url, headers_with_token, logger, description, invalid_field_payload, expected_status):
    # Step 1: Create valid booking
    valid_payload = {
        "firstname": "Valid",
        "lastname": "Payload",
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2023-01-01",
            "checkout": "2023-01-10"
        },
        "additionalneeds": "Lunch"
    }

    response = requests.post(f"{base_url}/booking", json=valid_payload)
    assert response.status_code == 200
    booking_id = response.json()["bookingid"]

    # Step 2: Merge invalid field into valid payload
    invalid_payload = valid_payload.copy()
    for key, val in invalid_field_payload.items():
        if key == "bookingdates":
            invalid_payload["bookingdates"] = valid_payload["bookingdates"].copy()
            invalid_payload["bookingdates"].update(val)
        else:
            invalid_payload[key] = val

    # Step 3: Send PUT request
    update_url = f"{base_url}/booking/{booking_id}"
    logger.info(f"{description} - PUT {update_url} with payload: {invalid_payload}")

    update_response = requests.put(
        update_url,
        headers=headers_with_token,
        json=invalid_payload
    )

    logger.info(f"Status Code: {update_response.status_code}")
    logger.debug(f"Response Body: {update_response.text}")

    # Step 4: Expect failure
    assert update_response.status_code == expected_status, (
        f"{description}: Expected {expected_status}, got {update_response.status_code}"
    )
