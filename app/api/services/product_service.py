from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ...database.functions.products.get_paginated import get_products_paginated_db
from ..schemas.v1.product import ProductListResponse, ProductSortBy, SortOrder


class ProductService:
    """Service layer for product operations"""

    @staticmethod
    async def get_products_list(
        db: AsyncSession,
        page: int = 1,
        size: int = 12,
        language_iso: str = "en",
        sort_by: ProductSortBy = ProductSortBy.CREATED_AT,
        sort_order: SortOrder = SortOrder.DESC,
        category_id: Optional[int] = None,
        tag_ids: Optional[list[int]] = None,
    ) -> ProductListResponse:
        """
        Get paginated list of products for homepage/category pages.

        Args:
            db: Database session
            page: Page number (1-based)
            size: Items per page (max 100)
            language_iso: Language for translations
            sort_by: Field to sort by
            sort_order: Sort direction
            category_id: Optional category filter
            tag_ids: Optional tag filters

        Returns:
            ProductListResponse with products and pagination
        """
        return await get_products_paginated_db(
            db=db,
            page=page,
            size=size,
            language_iso=language_iso,
            sort_by=sort_by.value,
            sort_order=sort_order.value,
            category_filter=category_id,
            tag_filter=tag_ids,
        )
