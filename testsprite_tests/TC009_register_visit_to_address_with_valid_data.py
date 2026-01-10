import requests
import random
import string

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
BUFFETS_URL = f"{BASE_URL}/api/v1/buffets"
OFICIOS_URL = f"{BASE_URL}/api/v1/oficios"
HEADERS_JSON = {"Content-Type": "application/json"}

def generate_unique_rut():
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

def test_register_visit_to_address_with_valid_data():
    session = requests.Session()
    session.timeout = 30

    # Login as admin to get JWT token using form-data (OAuth2 password flow)
    login_data = {
        "username": "admin@sistema.com",
        "password": "admin123"
    }
    try:
        login_resp = session.post(
            LOGIN_URL,
            data=login_data,
            timeout=30
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json().get("access_token") or login_resp.json().get("token") or login_resp.json().get("jwt")
        assert token, "JWT token not found in login response"
        auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Step 1: Create a new buffet (required to create oficio)
        unique_rut = generate_unique_rut()
        unique_email = f"testbuffet_tc009.{random.randint(10000,99999)}@example.com"
        buffet_payload = {
            "nombre": "Test Buffet TC009",
            "rut": unique_rut,
            "email_principal": unique_email
        }
        buffet_resp = session.post(BUFFETS_URL, json=buffet_payload, headers=auth_headers, timeout=30)
        assert buffet_resp.status_code == 201, f"Failed to create buffet: {buffet_resp.text}"
        buffet_id = buffet_resp.json().get("id")
        assert buffet_id, "Buffet ID not returned"

        # Step 2: Create a new oficio tied to the buffet
        oficio_payload = {
            "numero_oficio": f"TC009-{random.randint(10000,99999)}",
            "buffet_id": buffet_id,
            "vehiculo": {
                "patente": f"AAA{random.randint(100,999)}",
                "marca": "Toyota",
                "modelo": "Corolla",
                "año": 2020,
                "color": "Blanco"
            },
            "prioridad": "media"
        }
        oficio_resp = session.post(OFICIOS_URL, json=oficio_payload, headers=auth_headers, timeout=30)
        assert oficio_resp.status_code == 201, f"Failed to create oficio: {oficio_resp.text}"
        oficio_id = oficio_resp.json().get("id")
        assert oficio_id, "Oficio ID not returned"

        # Step 3: Add a direccion to the oficio
        direccion_payload = {
            "direccion": "Calle Falsa 123, Santiago",
            "comuna": "Santiago",
            "region": "Metropolitana",
            "tipo": "domicilio"
        }
        direccion_url = f"{OFICIOS_URL}/{oficio_id}/direcciones"
        direccion_resp = session.post(direccion_url, json=direccion_payload, headers=auth_headers, timeout=30)
        assert direccion_resp.status_code == 201, f"Failed to add direccion: {direccion_resp.text}"
        direccion_id = direccion_resp.json().get("id")
        assert direccion_id, "Direccion ID not returned"

        # Step 4: Register a visit with valid resultado and optional notes, lat, long
        visit_payload = {
            "resultado": "exitosa",
            "notas": "Visita realizada satisfactoriamente.",
            "latitud": "-33.4489",
            "longitud": "-70.6693"
        }
        visit_url = f"{BASE_URL}/api/v1/oficios/direcciones/{direccion_id}/visitas"
        visit_resp = session.post(visit_url, json=visit_payload, headers=auth_headers, timeout=30)
        assert visit_resp.status_code == 201, f"Failed to register visit: {visit_resp.text}"

    finally:
        # Clean up the created resources in reverse order ignoring errors
        try:
            if 'direccion_id' in locals():
                # No delete endpoint in PRD for direccion, so we skip this cleanup because not specified
                pass
        except Exception:
            pass
        try:
            if 'oficio_id' in locals():
                session.delete(f"{OFICIOS_URL}/{oficio_id}", headers=auth_headers, timeout=30)
        except Exception:
            pass
        try:
            if 'buffet_id' in locals():
                session.delete(f"{BUFFETS_URL}/{buffet_id}", headers=auth_headers, timeout=30)
        except Exception:
            pass

test_register_visit_to_address_with_valid_data()
