from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db

# Type aliases for common dependencies
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]


# Pagination dependency with validation
def get_pagination_params(
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 12,
) -> tuple[int, int]:
    return page, size


PaginationDep = Annotated[tuple[int, int], Depends(get_pagination_params)]


# Language dependency for i18n
def get_language(
    lang: Annotated[
        str, Query(regex=r"^[a-z]{2}$", description="Language ISO code")
    ] = "en",
) -> str:
    return lang


LanguageDep = Annotated[str, Depends(get_language)]
