import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
ME_URL = f"{BASE_URL}/api/v1/auth/me"
TIMEOUT = 30

def test_get_current_user_with_valid_token():
    login_data = {
        "username": "admin@sistema.com",
        "password": "admin123"
    }
    headers_login = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Authenticate to get JWT token
    try:
        login_response = requests.post(LOGIN_URL, data=login_data, headers=headers_login, timeout=TIMEOUT)
        assert login_response.status_code == 200, f"Login failed with status code {login_response.status_code}"
        token = login_response.json().get("access_token")
        assert token, "No access_token found in login response"
    except requests.RequestException as e:
        assert False, f"Login request exception: {e}"

    # Use token to get current authenticated user info
    headers_me = {
        "Authorization": f"Bearer {token}"
    }
    try:
        me_response = requests.get(ME_URL, headers=headers_me, timeout=TIMEOUT)
        assert me_response.status_code == 200, f"GET /auth/me failed with status code {me_response.status_code}"
        user_data = me_response.json()
        # Validate expected user fields present
        assert "email" in user_data, "User data missing 'email'"
        assert user_data["email"] == "admin@sistema.com", "User email does not match admin"
        assert "nombre" in user_data, "User data missing 'nombre'"
        assert "rol" in user_data, "User data missing 'rol'"
    except requests.RequestException as e:
        assert False, f"/auth/me request exception: {e}"

test_get_current_user_with_valid_token()