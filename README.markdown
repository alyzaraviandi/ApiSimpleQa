# RESTful Booker QA

This project is a comprehensive API test automation suite for the [RESTful Booker](https://restful-booker.herokuapp.com/) API. Built using **Python**, **pytest**, and **requests**, it validates the API's behavior and reliability through **positive** and **negative** test cases.

## 📌 Project Goals

- Verify core booking functionalities (create, read, update, delete) work as expected.
- Confirm proper authentication flow using tokens.
- Validate graceful handling of invalid inputs.
- Ensure correct validation of query parameters and payload data types.
- Identify issues like weak validation, inconsistent status codes, or unexpected behavior.

## 🧰 Tech Stack

- **Python 3.10+**
- **pytest**: Organizes and runs tests.
- **requests**: Sends HTTP requests.
- **logging**: Enhances debugging and traceability.

## ✅ Key Test Categories

### 🔐 Authentication
- Valid token generation.
- Invalid credentials and missing fields (XFAIL if API lacks validation).

### 📦 Create Booking
- Valid booking creation.
- Invalid data types (e.g., integers for names, strings for prices).
- Missing required fields.

### 📄 Get Bookings
- Fetch all bookings.
- Filter by name and date.
- Invalid query parameters (e.g., `first_name` instead of `firstname`).
- Invalid or malformed date formats.

### 🧾 Get Booking by ID
- Existing booking ID.
- Non-existent, negative, or string IDs.

### 🛠️ Update Booking (PUT & PATCH)
- Full and partial updates.
- Valid and invalid field types.
- Unauthorized or missing token scenarios.

### ❌ Delete Booking
- Successful deletion.
- Unauthorized attempts (no token, invalid token).
- Deletion of non-existent booking IDs.

## Known API Issues (Expected Failures)

Some tests are marked with `@pytest.mark.xfail` due to known issues in the RESTful Booker API:
- Accepts incorrect data types (e.g., `totalprice` as a string).
- Allows unknown query keys (e.g., `first_name`).
- Weak or nonexistent validation for missing fields.
- Permits invalid or malformed date values.
- Returns `200 OK` instead of appropriate error codes (e.g., `401`, `400`, `500`).

## 🚀 Setup & Usage Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run tests:
   ```bash
   pytest -v
   ```

## 📜 License

[MIT License](LICENSE)