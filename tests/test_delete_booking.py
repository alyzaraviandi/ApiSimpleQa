import requests
import pytest

# ---------------------- POSITIVE TESTS ----------------------

def test_delete_booking_success(base_url, headers_with_token, logger):
    # Step 1: Create a booking to delete
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

    response = requests.post(f"{base_url}/booking", json=payload)
    assert response.status_code == 200
    booking_id = response.json()["bookingid"]
    logger.info(f"Created booking for deletion: {booking_id}")

    # Step 2: Delete
    delete_response = requests.delete(
        f"{base_url}/booking/{booking_id}",
        headers=headers_with_token
    )
    logger.info(f"DELETE /booking/{booking_id} -> {delete_response.status_code}")
    logger.debug(delete_response.text)

    assert delete_response.status_code in [200, 201], "Expected successful deletion"

    # Step 3: Confirm Deletion
    confirm_response = requests.get(f"{base_url}/booking/{booking_id}")
    assert confirm_response.status_code == 404, "Booking still exists after deletion"

# ---------------------- NEGATIVE TESTS ----------------------

@pytest.mark.parametrize("description,booking_id,headers,expected_status", [
    ("Delete non-existent booking", 999999, {"Content-Type": "application/json"}, 403),  # Needs token
    ("Delete without token", 1, {}, 403),
    ("Delete with invalid token", 1, {"Cookie": "token=invalid"}, 403),
])
def test_delete_booking_negative_cases(base_url, logger, description, booking_id, headers, expected_status):
    url = f"{base_url}/booking/{booking_id}"
    logger.info(f"{description} - Attempting DELETE {url}")
    response = requests.delete(url, headers=headers)
    logger.info(f"Response: {response.status_code} - {response.text}")
    assert response.status_code == expected_status, f"{description} failed (got {response.status_code})"
