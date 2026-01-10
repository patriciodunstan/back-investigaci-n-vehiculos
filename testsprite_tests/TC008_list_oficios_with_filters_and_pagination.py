import requests
import random
import string

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
OFICIOS_URL = f"{BASE_URL}/api/v1/oficios"

ADMIN_USERNAME = "admin@sistema.com"
ADMIN_PASSWORD = "admin123"

def generate_valid_rut():
    """Genera un RUT chileno válido con dígito verificador correcto."""
    num = random.randint(10000000, 99999999)
    reversed_digits = [int(d) for d in str(num)[::-1]]
    factors = [2, 3, 4, 5, 6, 7]
    total = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
    remainder = 11 - (total % 11)
    if remainder == 11:
        dv = '0'
    elif remainder == 10:
        dv = 'K'
    else:
        dv = str(remainder)
    return f"{num}-{dv}"

def test_list_oficios_with_filters_and_pagination():
    # Authenticate as admin to get JWT token using form-data (OAuth2 password flow)
    try:
        login_resp = requests.post(
            LOGIN_URL,
            data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            timeout=30
        )
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}"
        token = login_resp.json().get("access_token")
        assert token is not None, "No access_token found in login response"
        headers = {"Authorization": f"Bearer {token}"}

        # Create a valid unique rut for buffet
        buffet_rut = generate_valid_rut()
        unique_email = f"testbuffet.{random.randint(10000,99999)}@example.com"

        # Create a buffet (admin only)
        buffet_data = {
            "nombre": "Test Buffet for Oficios",
            "rut": buffet_rut,
            "email_principal": unique_email
        }
        create_buffet_resp = requests.post(f"{BASE_URL}/api/v1/buffets", json=buffet_data, headers=headers, timeout=30)
        assert create_buffet_resp.status_code == 201, f"Buffet creation failed with status {create_buffet_resp.status_code}"
        buffet_id = create_buffet_resp.json().get("id")
        assert buffet_id is not None, "Created buffet id not returned"

        # Create oficio linked to buffet
        oficio_data = {
            "numero_oficio": f"TEST{random.randint(100000,999999)}",
            "buffet_id": buffet_id,
            "vehiculo": {
                "patente": f"ABC{random.randint(100,999)}",
                "marca": "Toyota",
                "modelo": "Corolla",
                "año": 2020,
                "color": "Blanco"
            },
            "prioridad": "media"
        }
        create_oficio_resp = requests.post(OFICIOS_URL, json=oficio_data, headers=headers, timeout=30)
        assert create_oficio_resp.status_code == 201, f"Oficio creation failed status {create_oficio_resp.status_code}"
        oficio = create_oficio_resp.json()
        oficio_id = oficio.get("id") or oficio.get("oficio_id")
        assert oficio_id is not None, "No oficio_id returned after creation"

        # For investigador_id, get current user id
        current_user_resp = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers, timeout=30)
        assert current_user_resp.status_code == 200, "Failed to get current user"
        current_user = current_user_resp.json()
        investigador_id = current_user.get("id")
        assert investigador_id is not None, "Current user id not found"

        # Test filtered list of oficios
        params = {
            "buffet_id": buffet_id,
            "skip": 0,
            "limit": 5
        }
        list_resp = requests.get(OFICIOS_URL, headers=headers, params=params, timeout=30)
        assert list_resp.status_code == 200, f"Failed to list oficios with filters, got {list_resp.status_code}: {list_resp.text}"
        oficios_list = list_resp.json()

        assert isinstance(oficios_list, (list, dict)), "Response is not a list or dict"
        if isinstance(oficios_list, dict):
            items = oficios_list.get("items") or oficios_list.get("results") or oficios_list.get("data") or oficios_list.get("oficios")
            if items is not None:
                oficios = items
            else:
                oficios = [oficios_list]
        else:
            oficios = oficios_list

        assert len(oficios) <= 5, "Returned more items than limit"

        # Validate only the filter we actually applied (buffet_id)
        for oficio_item in oficios:
            if "buffet_id" in oficio_item:
                assert oficio_item["buffet_id"] == buffet_id, "buffet_id filter mismatch"

        print(f"TC008 PASSED - Listed {len(oficios)} oficios with buffet_id filter")

    finally:
        if 'oficio_id' in locals():
            requests.delete(f"{OFICIOS_URL}/{oficio_id}", headers=headers, timeout=30)
        if 'buffet_id' in locals():
            requests.delete(f"{BASE_URL}/api/v1/buffets/{buffet_id}", headers=headers, timeout=30)


test_list_oficios_with_filters_and_pagination()