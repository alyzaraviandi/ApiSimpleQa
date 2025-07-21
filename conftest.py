import pytest
import requests
from utils.logger import get_logger  

@pytest.fixture(scope="session")
def logger():
    return get_logger("QA_Automation")  

@pytest.fixture(scope="session")
def base_url():
    return "https://restful-booker.herokuapp.com"

@pytest.fixture(scope="session")
def auth_token(base_url, logger):
    logger.info("Requesting auth token...")
    payload = {
        "username": "admin",
        "password": "password123"
    }
    response = requests.post(f"{base_url}/auth", json=payload)
    logger.debug(f"Auth response: {response.status_code} | {response.text}")
    assert response.status_code == 200
    token = response.json()["token"]
    logger.info("Auth token acquired.")
    return token

@pytest.fixture(scope="function")
def headers_with_token(auth_token):
    return {
        "Content-Type": "application/json",
        "Cookie": f"token={auth_token}"
    }
