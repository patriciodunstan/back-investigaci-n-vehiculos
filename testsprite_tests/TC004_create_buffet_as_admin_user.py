import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
BUFFETS_URL = f"{BASE_URL}/api/v1/buffets"
TIMEOUT = 30

def test_create_buffet_as_admin_user():
    # Step 1: Login as admin user with form data
    login_data = {
        "username": "admin@sistema.com",
        "password": "admin123"
    }
    headers_login = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        login_resp = requests.post(LOGIN_URL, data=login_data, headers=headers_login, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json().get("access_token")
        assert token, "No access_token in login response"
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"

    auth_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Define buffet data for creation with a valid RUT
    buffet_data = {
        "nombre": "Buffet Test Admin",
        "rut": "12345678-5",
        "email_principal": "contacto@buffettest.com",
        "telefono": "+56912345678",
        "contacto_nombre": "Juan Perez"
    }

    buffet_id = None

    # Create the buffet and then delete it finally
    try:
        create_resp = requests.post(BUFFETS_URL, json=buffet_data, headers=auth_headers, timeout=TIMEOUT)
        assert create_resp.status_code == 201, f"Buffet creation failed: {create_resp.status_code}, {create_resp.text}"
        buffet_resp_json = create_resp.json()
        buffet_id = buffet_resp_json.get("id")
        assert buffet_id is not None, "Created buffet ID not returned"

    except requests.RequestException as e:
        assert False, f"Buffet creation request failed: {e}"

    finally:
        if buffet_id:
            # Cleanup: soft delete the created buffet to keep tests idempotent
            delete_url = f"{BUFFETS_URL}/{buffet_id}"
            try:
                delete_resp = requests.delete(delete_url, headers=auth_headers, timeout=TIMEOUT)
                assert delete_resp.status_code == 204, f"Buffet delete failed: {delete_resp.status_code}, {delete_resp.text}"
            except requests.RequestException as e:
                # Log failure but do not fail the test here
                print(f"Warning: Buffet deletion failed in cleanup: {e}")

test_create_buffet_as_admin_user()
