from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, Query, status

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
    import traceback

    try:
        print("=== PRODUCTS ENDPOINT DEBUG ===")
        print(f"Database session: {db}")
        print(f"Pagination: {pagination}")
        print(f"Language: {language}")
        print(f"Category ID: {category_id}")
        print(f"Tag IDs: {tag_ids}")
        print(f"Sort by: {sort_by}")
        print(f"Sort order: {sort_order}")

        page, size = pagination
        print(f"Extracted page: {page}, size: {size}")

        print("About to call ProductService.get_products_list...")

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

        print(f"ProductService returned: {type(result)}")
        print("=== PRODUCTS ENDPOINT SUCCESS ===")
        return result

    except Exception as e:
        print(f"=== PRODUCTS ENDPOINT ERROR ===")
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        print("=== END ERROR ===")

        # Re-raise with original error for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug: {str(e)}",
        ) from e
