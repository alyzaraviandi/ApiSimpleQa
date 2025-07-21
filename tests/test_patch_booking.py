import requests
import pytest

# ---------------------- HAPPY PATH ----------------------


def test_patch_booking_success(base_url, headers_with_token, logger):
    # Step 1: Create a new booking
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

    create_response = requests.post(f"{base_url}/booking", json=create_payload)
    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]
    logger.info(f"Created booking: {booking_id}")

    # Step 2: Patch only firstname and lastname
    patch_payload = {
        "firstname": "James",
        "lastname": "Brown"
    }

    patch_response = requests.patch(
        f"{base_url}/booking/{booking_id}",
        headers=headers_with_token,
        json=patch_payload
    )

    logger.info(
        f"PATCH /booking/{booking_id} - Status: {patch_response.status_code}")
    logger.debug(patch_response.text)

    assert patch_response.status_code == 200
    updated = patch_response.json()
    assert updated["firstname"] == "James"
    assert updated["lastname"] == "Brown"


# ---------------------- NEGATIVE PATHS ----------------------

def test_patch_booking_with_invalid_token(base_url, logger):
    # Create booking to attempt patch on
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "totalprice": 123,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2022-01-01",
            "checkout": "2022-01-05"
        },
        "additionalneeds": "None"
    }
    create_response = requests.post(f"{base_url}/booking", json=payload)
    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    # Attempt PATCH with bad token
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": "token=INVALIDTOKEN123"
    }

    patch_payload = {"firstname": "Jane"}

    patch_response = requests.patch(
        f"{base_url}/booking/{booking_id}",
        headers=headers,
        json=patch_payload
    )

    logger.info(
        f"PATCH /booking/{booking_id} with invalid token - Status: {patch_response.status_code}")
    logger.debug(patch_response.text)

    assert patch_response.status_code == 403

def test_patch_nonexistent_booking(base_url, headers_with_token, logger):
    nonexistent_id = 999999
    patch_payload = {"firstname": "Ghost"}

    response = requests.patch(
        f"{base_url}/booking/{nonexistent_id}",
        headers=headers_with_token,
        json=patch_payload
    )

    logger.info(
        f"PATCH /booking/{nonexistent_id} - Status: {response.status_code}")
    logger.debug(response.text)

    # Can be 404 or 405 depending on how the API is implemented
    assert response.status_code in [404, 405]


def test_patch_booking_without_token(base_url, logger):
    # Create booking
    payload = {
        "firstname": "Anna",
        "lastname": "Smith",
        "totalprice": 222,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2023-05-01",
            "checkout": "2023-05-07"
        },
        "additionalneeds": "Dinner"
    }
    response = requests.post(f"{base_url}/booking", json=payload)
    assert response.status_code == 200
    booking_id = response.json()["bookingid"]

    # Patch with no token at all
    patch_payload = {"firstname": "Annabelle"}
    patch_response = requests.patch(
        f"{base_url}/booking/{booking_id}",
        json=patch_payload,
        headers={"Content-Type": "application/json",
                 "Accept": "application/json"}
    )

    logger.info(
        f"PATCH /booking/{booking_id} with no token - Status: {patch_response.status_code}")
    logger.debug(patch_response.text)

    assert patch_response.status_code == 403


@pytest.mark.parametrize("description,patch_payload,expected_status", [
    pytest.param(
        "Firstname as integer", {"firstname": 12345}, 400,
        marks=pytest.mark.xfail(reason="API accepts integer as firstname"),
    ),
    pytest.param(
        "Lastname as boolean", {"lastname": True}, 400,
        marks=pytest.mark.xfail(reason="API accepts boolean as lastname"),
    ),
    pytest.param(
        "Totalprice as string", {"totalprice": "four hundred"}, 400,
        marks=pytest.mark.xfail(reason="API accepts totalprice as string"),
    ),
    pytest.param(
        "Depositpaid as string", {"depositpaid": "yes"}, 400,
        marks=pytest.mark.xfail(reason="API accepts depositpaid as string"),
    ),
    pytest.param(
        "Checkin date as integer", {"bookingdates": {"checkin": 20230701}}, 400,
        marks=pytest.mark.xfail(reason="API accepts integer as checkin date"),
    ),
    pytest.param(
        "Checkout date as boolean", {"bookingdates": {"checkout": False}}, 400,
        marks=pytest.mark.xfail(reason="API accepts boolean as checkout date"),
    ),
])
def test_patch_booking_with_invalid_data_types(base_url, headers_with_token, logger, description, patch_payload, expected_status):
    # Step 1: Create a valid booking
    valid_payload = {
        "firstname": "Eva",
        "lastname": "White",
        "totalprice": 400,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2023-01-01",
            "checkout": "2023-01-10"
        },
        "additionalneeds": "WiFi"
    }

    response = requests.post(f"{base_url}/booking", json=valid_payload)
    assert response.status_code == 200
    booking_id = response.json()["bookingid"]

    # Step 2: Patch with invalid data
    patch_url = f"{base_url}/booking/{booking_id}"
    logger.info(f"{description} - PATCH {patch_url} with payload: {patch_payload}")

    patch_response = requests.patch(patch_url, headers=headers_with_token, json=patch_payload)

    logger.info(f"Status Code: {patch_response.status_code}")
    logger.debug(f"Response Body: {patch_response.text}")

    assert patch_response.status_code == expected_status, (
        f"{description}: Expected {expected_status}, got {patch_response.status_code}"
    )
