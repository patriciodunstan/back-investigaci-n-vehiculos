"""Dependencies compartidas de FastAPI"""

from .auth import (
    oauth2_scheme,
    get_current_user_id,
    require_auth,
)
from .pagination import (
    PaginationParams,
    get_pagination,
)

__all__ = [
    "oauth2_scheme",
    "get_current_user_id",
    "require_auth",
    "PaginationParams",
    "get_pagination",
]
