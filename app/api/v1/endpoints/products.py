from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....api.schemas.v1.product import ProductListResponse, ProductSortBy, SortOrder
from ....api.services.product_service import ProductService
from ....core.dependencies import DatabaseDep, LanguageDep, PaginationDep

router = APIRouter()


@router.get(
    "/",
    response_model=ProductListResponse,
    summary="Get paginated product list",
    description="Retrieve a paginated list of products for homepage or category browsing",
)
async def get_products(
    db: DatabaseDep,
    pagination: PaginationDep,
    language: LanguageDep,
    category_id: Annotated[
        Optional[int], Query(description="Filter by category ID", ge=1)
    ] = None,
    tag_ids: Annotated[
        Optional[list[int]], Query(description="Filter by tag IDs")
    ] = None,
    sort_by: Annotated[
        ProductSortBy, Query(description="Field to sort by")
    ] = ProductSortBy.CREATED_AT,
    sort_order: Annotated[
        SortOrder, Query(description="Sort direction")
    ] = SortOrder.DESC,
) -> ProductListResponse:
    """
    Get a paginated list of products.

    This endpoint is optimized for homepage and category listing views.
    It returns essential product information along with category details,
    variant indicators, and related data counts.

    **Query Parameters:**
    - `page`: Page number (starting from 1)
    - `size`: Number of items per page (1-100)
    - `lang`: Language code for translations (en, fr, es)
    - `category_id`: Filter products by category
    - `tag_ids`: Filter products by multiple tag IDs
    - `sort_by`: Sort field (created_at, price, name)
    - `sort_order`: Sort direction (ASC, DESC)

    **Response includes:**
    - Product list with category information
    - Pagination metadata
    - Variant and customization indicators
    - Related data counts (attributes, tags, images)
    """
    try:
        page, size = pagination

        result = await ProductService.get_products_list(
            db=db,
            page=page,
            size=size,
            language_iso=language,
            sort_by=sort_by,
            sort_order=sort_order,
            category_id=category_id,
            tag_ids=tag_ids,
        )

        return result

    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products. Please try again.",
        ) from e
