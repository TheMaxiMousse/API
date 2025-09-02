from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ....api.schemas.v1.product import (
    PaginationInfo,
    ProductListItem,
    ProductListResponse,
)


async def get_products_paginated_db(
    db: AsyncSession,
    page: int = 1,
    size: int = 12,
    language_iso: str = "en",
    sort_by: str = "created_at",
    sort_order: str = "DESC",
    category_filter: int | None = None,
    tag_filter: list[int] | None = None,
) -> ProductListResponse:
    """
    Python wrapper for the get_products_paginated PostgreSQL function.

    Args:
        db: Database session
        page: Page number (1-based)
        size: Items per page
        language_iso: Language code for translations
        sort_by: Field to sort by
        sort_order: Sort direction
        category_filter: Optional category ID filter
        tag_filter: Optional list of tag IDs to filter by

    Returns:
        ProductListResponse with products and pagination info
    """

    # Prepare parameters for the PostgreSQL function
    params = {
        "p_page": page,
        "p_size": size,
        "p_language_iso": language_iso,
        "p_sort_by": sort_by,
        "p_sort_order": sort_order,
        "p_category_filter": category_filter,
        "p_tag_filter": tag_filter,
    }

    # Call the PostgreSQL function
    query = text(
        """
        SELECT * FROM get_products_paginated(
            p_page := :p_page,
            p_size := :p_size,
            p_language_iso := :p_language_iso,
            p_sort_by := :p_sort_by,
            p_sort_order := :p_sort_order,
            p_category_filter := :p_category_filter,
            p_tag_filter := :p_tag_filter
        )
    """
    )

    result = await db.execute(query, params)
    rows = result.fetchall()

    if not rows:
        return ProductListResponse(
            products=[],
            pagination=PaginationInfo(
                current_page=page,
                page_size=size,
                total_items=0,
                total_pages=0,
                has_next=False,
                has_previous=False,
            ),
        )

    # Extract pagination info from first row (all rows have same pagination data)
    first_row = rows[0]
    pagination_data = first_row.pagination

    # Convert rows to ProductListItem objects
    products = []
    for row in rows:
        # Build category object
        category = {
            "category_id": row.category_id,
            "category_name": row.category_name,
            "category_color": row.category_color,
            "category_description": row.category_description,
        }

        # Build product object
        product = ProductListItem(
            product_id=row.product_id,
            product_name=row.product_name,
            product_description=row.product_description,
            product_type=row.product_type,
            price=row.price,
            base_price=row.base_price,
            image_url=row.image_url,
            preparation_time_hours=row.preparation_time_hours,
            min_order_hours=row.min_order_hours,
            serving_info=row.serving_info,
            is_customizable=row.is_customizable,
            created_at=row.created_at,
            category=category,
            has_variants=row.has_variants,
            default_variant_id=row.default_variant_id,
            variant_count=row.variant_count,
            attribute_count=row.attribute_count,
            tag_count=row.tag_count,
            image_count=row.image_count,
        )
        products.append(product)

    # Convert PostgreSQL pagination_info to Pydantic model
    pagination = PaginationInfo(
        current_page=pagination_data.current_page,
        page_size=pagination_data.page_size,
        total_items=pagination_data.total_items,
        total_pages=pagination_data.total_pages,
        has_next=pagination_data.has_next,
        has_previous=pagination_data.has_previous,
    )

    return ProductListResponse(products=products, pagination=pagination)
