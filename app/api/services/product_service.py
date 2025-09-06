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

    @staticmethod
    async def create_product(db: AsyncSession, product_data: dict) -> dict:
        """
        Create a new product in the database.

        Args:
            db: Database session
            product_data: Product data dictionary

        Returns:
            Dictionary with product_id and success message

        Raises:
            Exception: If product creation fails
        """
        import json

        from sqlalchemy import text

        # Prepare attributes as JSONB
        attributes_json = None
        if product_data.get("attributes"):
            attributes_json = json.dumps(
                [
                    {
                        "name": attr["name"],
                        "value": attr["value"],
                        "color": attr.get("color", "#32cd32"),
                    }
                    for attr in product_data["attributes"]
                ]
            )

        # Prepare translations as JSONB
        translations_json = None
        if product_data.get("translations"):
            translations_json = json.dumps(
                [
                    {
                        "language_iso": trans["language_iso"],
                        "name": trans["name"],
                        "description": trans.get("description", ""),
                    }
                    for trans in product_data["translations"]
                ]
            )

        # Prepare parameters for the stored procedure
        params = {
            "p_product_name": product_data["product_name"],
            "p_product_description": product_data["product_description"],
            "p_product_type": product_data["product_type"],
            "p_category_id": product_data["category_id"],
            "p_price": product_data.get("price"),
            "p_base_price": product_data.get("base_price"),
            "p_image_url": product_data.get("image_url"),
            "p_preparation_time_hours": product_data.get("preparation_time_hours", 48),
            "p_min_order_hours": product_data.get("min_order_hours", 48),
            "p_serving_info": product_data.get("serving_info"),
            "p_is_customizable": product_data.get("is_customizable", False),
            "p_tag_ids": product_data.get("tag_ids"),
            "p_attributes": attributes_json,
            "p_translations": translations_json,
            "p_created_by": product_data.get("created_by", "api"),
        }

        # Call the PostgreSQL function
        query = text(
            """
            SELECT add_new_product(
                :p_product_name,
                :p_product_description,
                :p_product_type,
                :p_category_id,
                :p_price,
                :p_base_price,
                :p_image_url,
                :p_preparation_time_hours,
                :p_min_order_hours,
                :p_serving_info,
                :p_is_customizable,
                :p_tag_ids,
                :p_attributes,
                :p_translations,
                :p_created_by
            )
        """
        )

        try:
            result = await db.execute(query, params)
            product_id = result.scalar()

            # Commit the transaction
            await db.commit()

            return {
                "product_id": product_id,
                "product_name": product_data["product_name"],
                "message": f"Product '{product_data['product_name']}' created successfully with ID {product_id}",
            }

        except Exception as e:
            await db.rollback()
            error_message = str(e)

            if "P0001" in error_message:
                raise ValueError("Product name cannot be empty")
            elif "P0002" in error_message:
                raise ValueError("Product description cannot be empty")
            elif "P0003" in error_message:
                raise ValueError("Product name must be at least 3 characters long")
            elif "P0004" in error_message:
                raise ValueError("Product name cannot exceed 200 characters")
            elif "P0005" in error_message:
                raise ValueError("Product name contains invalid characters")
            elif "P0011" in error_message:
                raise ValueError("Invalid or disabled category ID")
            elif "P0012" in error_message:
                raise ValueError("Invalid image URL format")
            elif "P0013" in error_message:
                raise ValueError("A product with this name already exists")
            elif "P0014" in error_message:
                raise ValueError("Invalid or disabled tag ID")
            else:
                raise Exception(f"Failed to create product: {error_message}")
