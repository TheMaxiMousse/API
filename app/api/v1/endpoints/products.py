from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Body, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from ....api.schemas.v1.product import (
    CreateProductRequest,
    CreateProductResponse,
    ProductListResponse,
    ProductSortBy,
    SortOrder,
)
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


@router.post(
    "",
    response_model=CreateProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Create a new product/recipe in the database with optional translations and attributes",
)
async def create_product(
    db: DatabaseDep,
    product: Annotated[
        CreateProductRequest,
        Body(
            ...,
            example={
                "product_name": "Chocolate Truffle Cake",
                "product_description": "Rich chocolate cake with Belgian chocolate ganache",
                "product_type": "standard",
                "category_id": 1,
                "price": 45.99,
                "image_url": "https://example.com/images/chocolate-cake.jpg",
                "preparation_time_hours": 24,
                "min_order_hours": 24,
                "serving_info": "8-10 persons",
                "is_customizable": False,
                "tag_ids": [1, 2],
                "attributes": [
                    {"name": "allergen", "value": "gluten", "color": "#FF6B6B"},
                    {"name": "allergen", "value": "dairy", "color": "#FF6B6B"},
                    {"name": "flavor", "value": "chocolate", "color": "#8B4513"},
                ],
                "translations": [
                    {
                        "language_iso": "fr",
                        "name": "Gâteau aux Truffes au Chocolat",
                        "description": "Gâteau au chocolat riche avec ganache au chocolat belge",
                    }
                ],
            },
        ),
    ],
) -> CreateProductResponse:
    """
    Create a new product with the following features:

    - **Validation**: Comprehensive input validation including XSS prevention
    - **Product Types**: Support for standard, configurable, and variant-based products
    - **Pricing**: Automatic price/base_price validation based on product type
    - **Internationalization**: Support for multiple language translations
    - **Attributes**: Add allergens, dietary info, flavors, etc.
    - **Tags**: Assign marketing tags like "seasonal", "bestseller"
    - **Security**: Input sanitization and SQL injection prevention

    Returns the created product ID and confirmation message.
    """
    try:
        # Convert Pydantic model to dict for service layer
        product_data = product.model_dump(exclude_none=True)

        # Call service to create product
        result = await ProductService.create_product(db, product_data)

        # Return response with created product info
        return CreateProductResponse(
            product_id=result["product_id"],
            product_name=result["product_name"],
            message=result["message"],
            created_at=datetime.now(),
        )

    except ValueError as e:
        # Handle validation errors from the database function
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError as e:
        # Handle database integrity errors
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product creation failed due to data conflict. Please check if the product name already exists.",
        )
    except Exception as e:
        # Log the error (in production, you'd use proper logging)
        print(f"Error creating product: {str(e)}")

        # Return generic error to client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product. Please try again or contact support if the issue persists.",
        )
