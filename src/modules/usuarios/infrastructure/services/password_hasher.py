"""
Servicio de hash de contrasenas.

Utiliza bcrypt para hashear y verificar contrasenas de forma segura.

Principios aplicados:
- SRP: Solo maneja hash de contrasenas
- OCP: Facil de cambiar algoritmo si es necesario
"""

import bcrypt


class PasswordHasher:
    """
    Servicio para hashear y verificar contrasenas.

    Utiliza bcrypt con configuracion segura por defecto.
    """

    def __init__(self, rounds: int = 12):
        """
        Inicializa el hasher.

        Args:
            rounds: Factor de trabajo para bcrypt (default: 12)
        """
        self._rounds = rounds

    def hash(self, password: str) -> str:
        """
        Genera un hash seguro de la contrasena.

        Args:
            password: Contrasena en texto plano

        Returns:
            Hash bcrypt de la contrasena
        """
        # Convertir a bytes y truncar a 72 bytes (limite de bcrypt)
        password_bytes = password.encode("utf-8")[:72]

        # Generar salt y hash
        salt = bcrypt.gensalt(rounds=self._rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Retornar como string
        return hashed.decode("utf-8")

    def verify(self, password: str, password_hash: str) -> bool:
        """
        Verifica si una contrasena coincide con su hash.

        Args:
            password: Contrasena en texto plano
            password_hash: Hash almacenado

        Returns:
            True si coinciden, False en caso contrario
        """
        try:
            # Truncar a 72 bytes para consistencia con hash
            password_bytes = password.encode("utf-8")[:72]
            hash_bytes = password_hash.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False


# Instancia singleton para uso en toda la aplicacion
password_hasher = PasswordHasher()
