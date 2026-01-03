"""
Servicio de tokens JWT.

Genera y valida tokens JWT para autenticacion.

Principios aplicados:
- SRP: Solo maneja tokens JWT
- DIP: Depende de configuracion inyectada
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError

from src.core.config import get_settings
from src.shared.domain.enums import RolEnum


class JWTService:
    """
    Servicio para crear y validar tokens JWT.

    Attributes:
        secret_key: Clave secreta para firmar tokens
        algorithm: Algoritmo de firma (HS256)
        expire_minutes: Minutos hasta expiracion del token
    """

    def __init__(self):
        settings = get_settings()
        self._secret_key = settings.SECRET_KEY
        self._algorithm = settings.ALGORITHM
        self._expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(
        self,
        user_id: int,
        email: str,
        rol: RolEnum,
        buffet_id: Optional[int] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Crea un token de acceso JWT.

        Args:
            user_id: ID del usuario
            email: Email del usuario
            rol: Rol del usuario
            buffet_id: ID del buffet (si aplica)
            expires_delta: Tiempo de expiracion personalizado

        Returns:
            Token JWT como string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self._expire_minutes)

        payload = {
            "sub": str(user_id),  # Subject (user id)
            "email": email,
            "rol": rol.value,
            "buffet_id": buffet_id,
            "exp": expire,
            "iat": datetime.utcnow(),  # Issued at
            "type": "access",
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decodifica y valida un token JWT.

        Args:
            token: Token JWT a decodificar

        Returns:
            Payload del token si es valido, None si es invalido

        Raises:
            No lanza excepciones, retorna None si falla
        """
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except JWTError:
            return None

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        """
        Extrae el user_id de un token.

        Args:
            token: Token JWT

        Returns:
            user_id si el token es valido, None en caso contrario
        """
        payload = self.decode_token(token)
        if payload is None:
            return None

        try:
            return int(payload.get("sub", 0))
        except (ValueError, TypeError):
            return None

    def get_rol_from_token(self, token: str) -> Optional[RolEnum]:
        """
        Extrae el rol de un token.

        Args:
            token: Token JWT

        Returns:
            RolEnum si el token es valido, None en caso contrario
        """
        payload = self.decode_token(token)
        if payload is None:
            return None

        try:
            rol_str = payload.get("rol")
            return RolEnum(rol_str) if rol_str else None
        except ValueError:
            return None

    def is_token_expired(self, token: str) -> bool:
        """
        Verifica si un token ha expirado.

        Args:
            token: Token JWT

        Returns:
            True si expiro o es invalido, False si aun es valido
        """
        payload = self.decode_token(token)
        if payload is None:
            return True

        exp = payload.get("exp")
        if exp is None:
            return True

        return datetime.utcnow() > datetime.fromtimestamp(exp)


# Instancia singleton para uso en toda la aplicacion
jwt_service = JWTService()
