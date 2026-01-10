import requests
import uuid
import random

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
BUFFETS_URL = f"{BASE_URL}/api/v1/buffets"
TIMEOUT = 30

def generate_valid_rut():
    """Genera un RUT chileno válido con dígito verificador correcto."""
    # Generar número base aleatorio (7-8 dígitos)
    num = random.randint(10000000, 99999999)
    
    # Calcular dígito verificador
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

def test_soft_delete_buffet_as_admin():
    # Admin credentials
    admin_email = "admin@sistema.com"
    admin_password = "admin123"

    # Step 1: Authenticate as admin using form-data (OAuth2 password flow)
    login_data = {
        "username": admin_email,
        "password": admin_password
    }
    login_resp = requests.post(LOGIN_URL, data=login_data, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}"
    token = login_resp.json().get("access_token")
    assert token is not None, "JWT token not found in login response"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Generate unique rut (valid Chilean RUT) and email to avoid conflicts
    unique_rut = generate_valid_rut()
    unique_email = f"test.softdelete.{uuid.uuid4().hex[:6]}@example.com"

    # Step 2: Create a new buffet to delete
    buffet_payload = {
        "nombre": "Buffet Test Soft Delete",
        "rut": unique_rut,
        "email_principal": unique_email,
        "telefono": "123456789",
        "contacto_nombre": "Test Contact"
    }
    create_resp = requests.post(BUFFETS_URL, json=buffet_payload, headers=headers, timeout=TIMEOUT)
    assert create_resp.status_code == 201, f"Buffet creation failed with status {create_resp.status_code}"
    buffet_id = create_resp.json().get("id")
    if buffet_id is None:
        buffet_id = create_resp.json().get("buffet_id")
    assert buffet_id is not None, "Created buffet ID not returned"

    try:
        # Step 3: Delete (soft delete) the buffet by ID
        delete_resp = requests.delete(f"{BUFFETS_URL}/{buffet_id}", headers=headers, timeout=TIMEOUT)
        assert delete_resp.status_code == 204, f"Expected 204 on delete, got {delete_resp.status_code}"

        # Step 4: Verify buffet is marked as deleted
        get_resp = requests.get(f"{BUFFETS_URL}/{buffet_id}", headers=headers, timeout=TIMEOUT)
        assert get_resp.status_code == 200, f"Failed to get buffet after delete, status {get_resp.status_code}"
        buffet_data = get_resp.json()
        activo = buffet_data.get("activo")
        deleted_flag = (activo is False) or buffet_data.get("deleted") is True
        assert deleted_flag, "Buffet is not marked as deleted (activo still True or no deleted flag set)"
    finally:
        # Cleanup: forcibly delete the buffet if still exists to not pollute data
        requests.delete(f"{BUFFETS_URL}/{buffet_id}", headers=headers, timeout=TIMEOUT)

test_soft_delete_buffet_as_admin()
