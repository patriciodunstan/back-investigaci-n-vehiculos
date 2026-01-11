"""
Dependencies de autenticación.

Proporciona funciones para obtener el usuario actual y verificar permisos.

Principios aplicados:
- SRP: Solo maneja autenticación
- DIP: Depende de abstracciones (interfaces)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from typing import Optional

from src.core.config import get_settings
from src.shared.infrastructure.database import get_db

settings = get_settings()

# Esquema OAuth2 para obtener token del header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,  # No lanzar error automático si no hay token
)


async def get_current_user_id(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[int]:
    """
    Obtiene el ID del usuario actual desde el JWT token.

    Args:
        token: JWT token del header Authorization

    Returns:
        Optional[int]: ID del usuario si el token es válido, None si no hay token

    Raises:
        HTTPException: Si el token es inválido o expirado
    """
    if token is None:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: no contiene user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_auth(user_id: Optional[int] = Depends(get_current_user_id)) -> int:
    """
    Requiere que el usuario esté autenticado.

    Uso en endpoints:
        @router.get("/protected")
        async def protected_endpoint(user_id: int = Depends(require_auth)):
            return {"user_id": user_id}

    Args:
        user_id: ID del usuario (inyectado por get_current_user_id)

    Returns:
        int: ID del usuario autenticado

    Raises:
        HTTPException: Si no hay usuario autenticado
    """
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


# Placeholder para cuando tengamos el modelo Usuario
# async def get_current_user(
#     user_id: int = Depends(require_auth),
#     db: Session = Depends(get_db)
# ) -> "Usuario":
#     """Obtiene el usuario completo desde la BD"""
#     from src.modules.usuarios.infrastructure.models import UsuarioModel
#
#     user = db.query(UsuarioModel).filter(UsuarioModel.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Usuario no encontrado")
#     if not user.activo:
#         raise HTTPException(status_code=403, detail="Usuario inactivo")
#
#     return user
