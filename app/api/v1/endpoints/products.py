from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, Query, status

from ....api.schemas.v1.product import ProductListResponse, ProductSortBy, SortOrder
from ....api.services.product_service import ProductService
from ....core.dependencies import DatabaseDep, LanguageDep, PaginationDep

router = APIRouter()


@router.get(
    "",
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products. Please try again.",
        ) from e
