import requests
import uuid
import random

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
BUFFETS_URL = f"{BASE_URL}/api/v1/buffets"


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


def test_TC006_update_buffet_as_admin_user():
    session = requests.Session()
    timeout = 30

    # Generate valid RUT and unique email to avoid conflicts
    unique_rut = generate_valid_rut()
    unique_email = f"updatebuffet.{uuid.uuid4().hex[:6]}@test.com"

    # Admin credentials
    admin_username = "admin@sistema.com"
    admin_password = "admin123"

    # Step 1: Login as admin using application/x-www-form-urlencoded
    login_data = {
        "username": admin_username,
        "password": admin_password
    }
    headers_login = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    login_resp = session.post(LOGIN_URL, data=login_data, headers=headers_login, timeout=timeout)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json().get("access_token")
    assert token, "No access_token in login response"

    auth_header = {"Authorization": f"Bearer {token}"}

    # Step 2: Create a new buffet to update (using admin privileges)
    buffet_payload_create = {
        "nombre": "Buffet Test Update",
        "rut": unique_rut,
        "email_principal": unique_email,
        "telefono": "123456789",
        "contacto_nombre": "Test Contact"
    }
    create_resp = session.post(
        BUFFETS_URL,
        json=buffet_payload_create,
        headers={**auth_header, "Content-Type": "application/json"},
        timeout=timeout,
    )
    assert create_resp.status_code == 201, f"Buffet creation failed: {create_resp.text}"
    buffet_created = create_resp.json()
    buffet_id = buffet_created.get("id")
    assert buffet_id is not None, "Created buffet has no id"

    try:
        # Step 3: Update the created buffet using PUT /api/v1/buffets/{buffet_id}
        buffet_payload_update = {
            "nombre": "Buffet Test Updated",
            "rut": unique_rut,
            "email_principal": "updated@test.com",
            "telefono": "987654321",
            "contacto_nombre": "Updated Contact"
        }
        update_url = f"{BUFFETS_URL}/{buffet_id}"
        update_resp = session.put(
            update_url,
            json=buffet_payload_update,
            headers={**auth_header, "Content-Type": "application/json"},
            timeout=timeout,
        )
        assert update_resp.status_code == 200, f"Buffet update failed: {update_resp.text}"

        updated_buffet = update_resp.json()
        # Validate updated fields
        assert updated_buffet.get("nombre") == buffet_payload_update["nombre"], "Nombre not updated"
        # Assert rut unchanged from original creation (do not trust update payload rut)
        assert updated_buffet.get("rut") == buffet_created.get("rut"), "RUT mismatch after update"
        assert updated_buffet.get("email_principal") == buffet_payload_update["email_principal"], "email_principal not updated"
        assert updated_buffet.get("telefono") == buffet_payload_update["telefono"], "telefono not updated"
        assert updated_buffet.get("contacto_nombre") == buffet_payload_update["contacto_nombre"], "contacto_nombre not updated"

    finally:
        # Step 4: Cleanup - delete the created buffet
        delete_resp = session.delete(update_url, headers=auth_header, timeout=timeout)
        assert delete_resp.status_code == 204, f"Buffet deletion failed: {delete_resp.text}"


test_TC006_update_buffet_as_admin_user()
