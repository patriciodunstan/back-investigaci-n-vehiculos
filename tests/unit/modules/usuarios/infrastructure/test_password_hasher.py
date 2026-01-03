"""
Tests para PasswordHasher.

Verifica el hashing y verificación de contraseñas.
"""

import pytest

from src.modules.usuarios.infrastructure.services.password_hasher import PasswordHasher


class TestPasswordHasher:
    """Tests para PasswordHasher"""

    @pytest.fixture
    def hasher(self):
        """Instancia del password hasher"""
        return PasswordHasher()

    def test_hash_password(self, hasher):
        """Test que hash genera un hash diferente al password original"""
        password = "password123"
        hashed = hasher.hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert isinstance(hashed, str)

    def test_hash_diferentes_passwords_diferentes_hashes(self, hasher):
        """Test que diferentes passwords generan diferentes hashes"""
        password1 = "password123"
        password2 = "password456"

        hash1 = hasher.hash(password1)
        hash2 = hasher.hash(password2)

        assert hash1 != hash2

    def test_hash_mismo_password_diferentes_hashes(self, hasher):
        """Test que el mismo password genera diferentes hashes (por el salt)"""
        password = "password123"

        hash1 = hasher.hash(password)
        hash2 = hasher.hash(password)

        # Deben ser diferentes por el salt aleatorio
        assert hash1 != hash2

    def test_verify_password_correcta(self, hasher):
        """Test que verify retorna True para password correcto"""
        password = "password123"
        hashed = hasher.hash(password)

        assert hasher.verify(password, hashed) is True

    def test_verify_password_incorrecta(self, hasher):
        """Test que verify retorna False para password incorrecto"""
        password = "password123"
        hashed = hasher.hash(password)

        assert hasher.verify("password_incorrecta", hashed) is False

    def test_verify_hash_invalido(self, hasher):
        """Test que verify retorna False para hash inválido"""
        password = "password123"
        hash_invalido = "hash_invalido"

        assert hasher.verify(password, hash_invalido) is False

    def test_hash_password_largo(self, hasher):
        """Test que hash funciona con passwords largos"""
        password_largo = "a" * 100
        hashed = hasher.hash(password_largo)

        assert hasher.verify(password_largo, hashed) is True

    def test_hash_password_corto(self, hasher):
        """Test que hash funciona con passwords cortos"""
        password_corto = "abc"
        hashed = hasher.hash(password_corto)

        assert hasher.verify(password_corto, hashed) is True
