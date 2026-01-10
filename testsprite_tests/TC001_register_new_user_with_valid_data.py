import requests
import uuid

BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = "/api/v1/auth/register"
TIMEOUT = 30

def test_register_new_user_with_valid_data():
    unique_email = f"testuser_{uuid.uuid4().hex}@example.com"
    payload = {
        "email": unique_email,
        "password": "StrongPass123",
        "nombre": "Test User"
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            BASE_URL + REGISTER_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=TIMEOUT
        )
        assert response.status_code == 201, f"Expected status 201, got {response.status_code}. Response: {response.text}"
    finally:
        # Attempt to login and delete the created user if API supports delete user (not provided in PRD)
        # Since no delete user endpoint is provided, we leave cleanup here or could log this user to clean later.
        pass

test_register_new_user_with_valid_data()