import requests

def test_login_user_with_correct_credentials():
    url = "http://localhost:8000/api/v1/auth/login"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": "admin@sistema.com",
        "password": "admin123"
    }
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request to login endpoint failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    try:
        json_resp = response.json()
    except ValueError:
        assert False, "Response is not a valid JSON"

    assert "access_token" in json_resp or "token" in json_resp or "jwt" in json_resp, \
        "JWT token not found in the response."

test_login_user_with_correct_credentials()