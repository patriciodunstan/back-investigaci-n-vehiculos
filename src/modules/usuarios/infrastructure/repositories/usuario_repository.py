"""
Implementacion SQLAlchemy del repositorio de usuarios.

Principios aplicados:
- DIP: Implementa la interface IUsuarioRepository
- SRP: Solo maneja persistencia de usuarios
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.modules.usuarios.application.interfaces import IUsuarioRepository
from src.modules.usuarios.domain.entities import Usuario
from src.modules.usuarios.infrastructure.models import UsuarioModel
from src.shared.domain.value_objects import Email


class UsuarioRepository(IUsuarioRepository):
    """
    Repositorio de usuarios usando SQLAlchemy.

    Implementa todas las operaciones definidas en IUsuarioRepository.
    """

    def __init__(self, session: Session):
        self._session = session

    def _model_to_entity(self, model: UsuarioModel) -> Usuario:
        """Convierte modelo SQLAlchemy a entidad de dominio."""
        usuario = Usuario(
            email=Email.crear(model.email),
            nombre=model.nombre,
            password_hash=model.password_hash,
            rol=model.rol,
            buffet_id=model.buffet_id,
            activo=model.activo,
            avatar_url=model.avatar_url,
        )
        # Asignar campos de la base entity manualmente
        usuario.id = model.id
        usuario.create_at = model.created_at
        usuario.update_at = model.updated_at
        return usuario

    def _entity_to_model(self, entity: Usuario) -> UsuarioModel:
        """Convierte entidad de dominio a modelo SQLAlchemy."""
        model = UsuarioModel(
            email=entity.email_str,
            nombre=entity.nombre,
            password_hash=entity.password_hash,
            rol=entity.rol,
            buffet_id=entity.buffet_id,
            activo=entity.activo,
            avatar_url=entity.avatar_url,
        )
        if entity.id:
            model.id = entity.id
        return model

    async def get_by_id(self, user_id: int) -> Optional[Usuario]:
        """Obtiene usuario por ID."""
        stmt = select(UsuarioModel).where(UsuarioModel.id == user_id)
        result = self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """Obtiene usuario por email."""
        email_lower = email.lower().strip()
        stmt = select(UsuarioModel).where(UsuarioModel.email == email_lower)
        result = self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def exists_by_email(self, email: str) -> bool:
        """Verifica si existe usuario con email."""
        email_lower = email.lower().strip()
        stmt = (
            select(func.count())
            .select_from(UsuarioModel)
            .where(UsuarioModel.email == email_lower)
        )
        result = self._session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def add(self, usuario: Usuario) -> Usuario:
        """Agrega nuevo usuario."""
        model = UsuarioModel(
            email=usuario.email_str.lower(),
            nombre=usuario.nombre,
            password_hash=usuario.password_hash,
            rol=usuario.rol,
            buffet_id=usuario.buffet_id,
            activo=usuario.activo,
            avatar_url=usuario.avatar_url,
        )

        self._session.add(model)
        self._session.flush()  # Para obtener el ID

        return self._model_to_entity(model)

    async def update(self, usuario: Usuario) -> Usuario:
        """Actualiza usuario existente."""
        stmt = select(UsuarioModel).where(UsuarioModel.id == usuario.id)
        result = self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Usuario con ID {usuario.id} no encontrado")

        # Actualizar campos
        model.nombre = usuario.nombre
        model.rol = usuario.rol
        model.buffet_id = usuario.buffet_id
        model.activo = usuario.activo
        model.avatar_url = usuario.avatar_url

        self._session.flush()

        return self._model_to_entity(model)

    async def delete(self, user_id: int) -> bool:
        """Elimina usuario (soft delete)."""
        stmt = select(UsuarioModel).where(UsuarioModel.id == user_id)
        result = self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return False

        model.activo = False
        self._session.flush()

        return True

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        activo_only: bool = True,
    ) -> List[Usuario]:
        """Obtiene lista de usuarios."""
        stmt = select(UsuarioModel)

        if activo_only:
            stmt = stmt.where(UsuarioModel.activo == True)  # noqa: E712

        stmt = stmt.offset(skip).limit(limit)

        result = self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(m) for m in models]

    async def get_by_buffet(
        self,
        buffet_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Usuario]:
        """Obtiene usuarios de un buffet."""
        stmt = (
            select(UsuarioModel)
            .where(UsuarioModel.buffet_id == buffet_id)
            .where(UsuarioModel.activo == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
        )

        result = self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(m) for m in models]

    async def count(self, activo_only: bool = True) -> int:
        """Cuenta total de usuarios."""
        stmt = select(func.count(UsuarioModel.id))

        if activo_only:
            stmt = stmt.where(UsuarioModel.activo == True)  # noqa: E712

        result = self._session.execute(stmt)
        count = result.scalar()
        return count
