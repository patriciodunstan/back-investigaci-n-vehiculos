import pytest
from src.shared.domain.value_objects import RutChileno, Email, Patente


class TestRutChileno:
    """Tests para Rutchileno"""

    def test_rut_valido(self):
        """RUT válido se crea correctamente"""
        rut = RutChileno.crear("12345678-5")
        assert rut.numero == 12345678
        assert rut.digito_verificador == "5"

    def test_rut_con_puntos(self):
        """RUT con puntos se normaliza"""
        rut = RutChileno.crear("12.345.678-5")
        assert rut.numero == 12345678

    def test_rut_invalido_lanza_error(self):
        """Rut con dígito verificador incorrecto lanza error"""
        with pytest.raises(ValueError, match="Dígito verificador inválido"):
            RutChileno.crear("12345678-0")

    def test_rut_con_k(self):
        """RUT con dígito K funciona"""
        # 11.111.112-K es un RUT válido cuyo dígito verificador es K
        rut = RutChileno.crear("11111112-K")
        assert rut.digito_verificador == "K"


class TestEmail:
    """Tests para Email"""

    def test_email_valido(self):
        """Email válido se crea correctamente"""
        email = Email.crear("test@example.com")
        assert email.valor == "test@example.com"

    def test_email_normaliza__a_lowercase(self):
        """Email se normaliza a minúsculas"""
        email = Email.crear("Test@EXAMPLE.COM")
        assert email.valor == "test@example.com"

    def test_email_invalido_lanza_error(self):
        """Email inválido lanza error"""
        with pytest.raises(ValueError):
            Email.crear("no-es-email")


class TestPatente:
    """Tests para Patente"""

    def test_patente_formato_nuevo(self):
        """Patente formato nuevo se detecta"""
        patente = Patente.crear("ABCD12")
        assert patente.formato == "nuevo"

    def test_patente_formato_antiguo(self):
        """Patente formato antiguo se detecta"""
        patente = Patente.crear("AB1234")
        assert patente.formato == "antiguo"

    def test_patente_normaliza(self):
        """Patente se normaliza a mayúsculas"""
        patente = Patente.crear("abcd-12")
        assert patente.valor == "ABCD12"

    def test_patente_invalida_lanza_error(self):
        """
        Patente inválida lanza error
        """
        with pytest.raises(ValueError):
            Patente.crear("ABC123")
