import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
VEHICLE_QUERY_URL_TEMPLATE = f"{BASE_URL}/api/v1/investigaciones/boostr/vehiculo/{{patente}}"
TIMEOUT = 30

def test_query_vehicle_information_from_boostr_api():
    # Admin credentials as per instructions
    login_data = {
        'username': 'admin@sistema.com',
        'password': 'admin123'
    }
    headers_form = {'Content-Type': 'application/x-www-form-urlencoded'}
    # Login to get JWT token
    try:
        login_response = requests.post(LOGIN_URL, data=login_data, headers=headers_form, timeout=TIMEOUT)
        assert login_response.status_code == 200, f"Login failed with status {login_response.status_code}"
        token = login_response.json().get('access_token')
        assert token, "No access_token found in login response"
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"Login request failed: {e}")

    auth_headers = {
        'Authorization': f"Bearer {token}"
    }

    # Use a test license plate known to exist or try a generic one; since no test resource given, try a common dummy
    test_plates = ["ABC123", "ZZZ999", "NONEXISTENT123"]

    for patente in test_plates:
        url = VEHICLE_QUERY_URL_TEMPLATE.format(patente=patente)
        try:
            response = requests.get(url, headers=auth_headers, timeout=TIMEOUT)
        except requests.RequestException as e:
            raise AssertionError(f"Request to {url} failed: {e}")

        if response.status_code == 200:
            # On success, expect vehicle data returned as JSON dictionary
            try:
                data = response.json()
                # Check at least 'patente' field in response matches requested plate (case-insensitive)
                assert isinstance(data, dict), "Response JSON is not a dictionary"
                assert 'patente' in data or 'plate' in data, "Vehicle data missing 'patente' or equivalent field"
                # Accept case-insensitive match
                response_plate = data.get('patente') or data.get('plate')
                assert response_plate and response_plate.lower() == patente.lower(), \
                    f"Returned plate '{response_plate}' does not match requested plate '{patente}'"
            except (ValueError, AssertionError) as e:
                raise AssertionError(f"Invalid JSON response or data mismatch for plate '{patente}': {e}")
        elif response.status_code == 404:
            # Vehicle not found, expected for invalid plates
            try:
                error_json = response.json()
                # Optionally check error message presence
                assert isinstance(error_json, dict), "Error response JSON not a dictionary"
            except ValueError:
                # Response might not be JSON, still 404 is acceptable
                pass
        elif response.status_code == 429:
            # Rate limit exceeded response, verify response structure
            try:
                error_json = response.json()
                assert isinstance(error_json, dict), "429 response JSON not a dictionary"
            except ValueError:
                pass
        else:
            raise AssertionError(f"Unexpected HTTP status {response.status_code} for plate '{patente}'")

test_query_vehicle_information_from_boostr_api()