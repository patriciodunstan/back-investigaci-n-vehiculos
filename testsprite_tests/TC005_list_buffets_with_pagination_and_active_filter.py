import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
BUFFETS_URL = f"{BASE_URL}/api/v1/buffets"
TIMEOUT = 30

def test_list_buffets_with_pagination_and_active_filter():
    # Authenticate as admin to get JWT token
    login_data = {
        'username': 'admin@sistema.com',
        'password': 'admin123'
    }
    headers_login = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response_login = requests.post(LOGIN_URL, data=login_data, headers=headers_login, timeout=TIMEOUT)
    assert response_login.status_code == 200, f"Login failed with status {response_login.status_code}"
    token = response_login.json().get('access_token')
    assert token, "JWT token not found in login response"
    headers = {
        'Authorization': f"Bearer {token}"
    }

    # Test listing buffets with pagination and active filter
    params = {
        'skip': 0,
        'limit': 10,
        'activo_only': True
    }
    response = requests.get(BUFFETS_URL, headers=headers, params=params, timeout=TIMEOUT)

    assert response.status_code == 200, f"Failed to list buffets, status code {response.status_code}"

    data = response.json()
    # Validate pagination keys and buffet list format
    assert isinstance(data, dict), "Response is not a JSON object"
    # According to typical paginated responses, expect keys like items, total, skip, limit
    # Since the PRD doesn't explicitly mention response schema for buffets GET,
    # We validate that the result includes a list and pagination info

    # Check some common pagination keys if present
    # If not present, at least check that the data is a list or dict with 'items' key
    items = None
    if 'items' in data:
        items = data['items']
        # check pagination keys
        assert 'total' in data, "'total' key not found in response"
        assert 'skip' in data, "'skip' key not found in response"
        assert 'limit' in data, "'limit' key not found in response"
        assert isinstance(data['total'], int), "'total' is not int"
        assert isinstance(data['skip'], int), "'skip' is not int"
        assert isinstance(data['limit'], int), "'limit' is not int"
    else:
        # fallback: if response is list, treat as items
        assert isinstance(data, list), "Response is neither dict with items nor list"
        items = data

    # Validate that all buffets are active if filtering activo_only=True
    # Buffets probably have an 'activo' or 'activo_only' field, but PRD does not describe buffet fields explicitly
    # We will just check that for each buffet in items, if 'activo' present, it is True
    for buffet in items:
        if 'activo' in buffet:
            assert buffet['activo'] is True, "Buffet returned which is not active while activo_only=True"

test_list_buffets_with_pagination_and_active_filter()