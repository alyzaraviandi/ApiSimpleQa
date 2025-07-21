import requests
import pytest

# ---------------------- POSITIVE TESTS ----------------------

def test_get_booking_by_id_success(base_url, logger):
    """Happy path: Successfully retrieve booking by ID"""
    # Step 1: Create a new booking
    create_payload = {
        "firstname": "Sally",
        "lastname": "Brown",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2013-02-23",
            "checkout": "2014-10-23"
        },
        "additionalneeds": "Breakfast"
    }

    create_response = requests.post(f"{base_url}/booking", json=create_payload)
    assert create_response.status_code == 200, f"Booking creation failed: {create_response.text}"
    booking_id = create_response.json()["bookingid"]

    logger.info(f"Created booking with ID: {booking_id}")

    # Step 2: Get booking by ID
    headers = {"Accept": "application/json"}
    get_response = requests.get(f"{base_url}/booking/{booking_id}", headers=headers)

    logger.info(f"GET /booking/{booking_id} - Status Code: {get_response.status_code}")
    logger.debug(f"Booking Details: {get_response.text}")

    assert get_response.status_code == 200

    data = get_response.json()
    assert data["firstname"] == "Sally"
    assert data["lastname"] == "Brown"
    assert data["totalprice"] == 111
    assert data["depositpaid"] is True
    assert data["bookingdates"]["checkin"] == "2013-02-23"
    assert data["bookingdates"]["checkout"] == "2014-10-23"
    assert data["additionalneeds"] == "Breakfast"

# ---------------------- NEGATIVE TESTS ----------------------

@pytest.mark.parametrize("test_case, booking_id", [
    ("non-existent ID", 9999999),
    ("negative ID", -1),
    ("string ID", "abc123"),
])
def test_get_booking_invalid_id_formats(base_url, test_case, booking_id, logger):
    """Non-happy path: Request booking with invalid or non-existent ID"""
    url = f"{base_url}/booking/{booking_id}"
    logger.info(f"Testing {test_case} with ID: {booking_id}")
    response = requests.get(url, headers={"Accept": "application/json"})

    logger.debug(f"GET {url} - Status: {response.status_code} - Body: {response.text}")
    assert response.status_code == 404, f"{test_case}: Expected 404 but got {response.status_code}"
