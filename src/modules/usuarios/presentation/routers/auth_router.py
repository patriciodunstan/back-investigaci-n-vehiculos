"""
Router de autenticacion.

Endpoints para registro, login y gestion de sesion.

Principios aplicados:
- SRP: Solo endpoints de autenticacion
- Thin controller: Delega logica a use cases
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import get_db
from src.modules.usuarios.application.dtos import RegisterUserDTO, LoginDTO
from src.modules.usuarios.application.use_cases import (
    RegisterUserUseCase,
    LoginUserUseCase,
    GetCurrentUserUseCase,
)
from src.modules.usuarios.infrastructure.repositories import UsuarioRepository
from src.modules.usuarios.domain.exceptions import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    InactiveUserException,
    InvalidTokenException,
    UsuarioNotFoundException,
)
from src.modules.usuarios.presentation.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)


router = APIRouter(prefix="/auth", tags=["Autenticacion"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_usuario_repository(db: AsyncSession = Depends(get_db)) -> UsuarioRepository:
    """Dependency para obtener el repositorio de usuarios."""
    return UsuarioRepository(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    repository: UsuarioRepository = Depends(get_usuario_repository),
) -> UserResponse:
    """
    Dependency para obtener el usuario actual desde el token.

    Raises:
        HTTPException 401: Si el token es invalido o el usuario no existe
    """
    use_case = GetCurrentUserUseCase(repository)
    try:
        user_dto = await use_case.execute(token)
        return UserResponse(
            id=user_dto.id,
            email=user_dto.email,
            nombre=user_dto.nombre,
            rol=user_dto.rol,
            buffet_id=user_dto.buffet_id,
            activo=user_dto.activo,
            avatar_url=user_dto.avatar_url,
            created_at=user_dto.created_at,
            updated_at=user_dto.updated_at,
        )
    except (
        InvalidTokenException,
        UsuarioNotFoundException,
        InactiveUserException,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea un nuevo usuario en el sistema",
)
async def register(
    request: RegisterRequest,
    repository: UsuarioRepository = Depends(get_usuario_repository),
):
    """
    Registra un nuevo usuario.

    - **email**: Email unico del usuario
    - **password**: Contrasena (minimo 6 caracteres)
    - **nombre**: Nombre completo
    - **rol**: Rol del usuario (admin, investigador, cliente)
    - **buffet_id**: ID del buffet (requerido para clientes)
    """
    use_case = RegisterUserUseCase(repository)

    dto = RegisterUserDTO(
        email=request.email,
        password=request.password,
        nombre=request.nombre,
        rol=request.rol,
        buffet_id=request.buffet_id,
    )

    try:
        user_dto = await use_case.execute(dto)
        return UserResponse(
            id=user_dto.id,
            email=user_dto.email,
            nombre=user_dto.nombre,
            rol=user_dto.rol,
            buffet_id=user_dto.buffet_id,
            activo=user_dto.activo,
            avatar_url=user_dto.avatar_url,
            created_at=user_dto.created_at,
            updated_at=user_dto.updated_at,
        )
    except EmailAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login de usuario",
    description="Autentica un usuario y retorna token JWT",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repository: UsuarioRepository = Depends(get_usuario_repository),
):
    """
    Autentica un usuario con email y password.

    Retorna un token JWT para usar en endpoints protegidos.
    """
    use_case = LoginUserUseCase(repository)

    dto = LoginDTO(
        email=form_data.username,  # OAuth2 usa 'username' para el email
        password=form_data.password,
    )

    try:
        token_dto = await use_case.execute(dto)
        return TokenResponse(
            access_token=token_dto.access_token,
            token_type=token_dto.token_type,
            expires_in=token_dto.expires_in,
        )
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InactiveUserException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )


@router.post(
    "/login/json",
    response_model=TokenResponse,
    summary="Login de usuario (JSON)",
    description="Login alternativo usando JSON en lugar de form-data",
)
async def login_json(
    request: LoginRequest,
    repository: UsuarioRepository = Depends(get_usuario_repository),
):
    """
    Login usando JSON body en lugar de form-data.

    Util para clientes que prefieren JSON.
    """
    use_case = LoginUserUseCase(repository)

    dto = LoginDTO(
        email=request.email,
        password=request.password,
    )

    try:
        token_dto = await use_case.execute(dto)
        return TokenResponse(
            access_token=token_dto.access_token,
            token_type=token_dto.token_type,
            expires_in=token_dto.expires_in,
        )
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasena incorrectos",
        )
    except InactiveUserException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Usuario actual",
    description="Obtiene los datos del usuario autenticado",
)
async def get_me(
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Retorna los datos del usuario actual.

    Requiere autenticacion con token JWT.
    """
    return current_user
