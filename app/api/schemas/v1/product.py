from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ....api.schemas.base import PaginationInfo


class ProductType(str, Enum):
    STANDARD = "standard"
    CONFIGURABLE = "configurable"
    VARIANT_BASED = "variant_based"


class CategoryResponse(BaseModel):
    category_id: int
    category_name: str
    category_color: str
    category_description: Optional[str] = None


class ProductListItem(BaseModel):
    """Product item for listing views (homepage, category pages)"""

    model_config = ConfigDict(from_attributes=True)

    # Core product data
    product_id: int
    product_name: str
    product_description: str
    product_type: ProductType
    price: Optional[float] = Field(
        None, description="Price for standard/variant products"
    )
    base_price: Optional[float] = Field(
        None, description="Base price for configurable products"
    )
    image_url: Optional[str] = None
    preparation_time_hours: int
    min_order_hours: int
    serving_info: Optional[str] = None
    is_customizable: bool
    created_at: datetime

    # Category information
    category: CategoryResponse

    # Variant indicators
    has_variants: bool = Field(..., description="Whether product has variants")
    default_variant_id: Optional[int] = Field(
        None, description="Default variant ID if applicable"
    )
    variant_count: int = Field(0, description="Number of variants")

    # Related data counts
    attribute_count: int = Field(0, description="Number of attributes")
    tag_count: int = Field(0, description="Number of tags assigned")
    image_count: int = Field(0, description="Number of additional images")


class ProductListResponse(BaseModel):
    """Response for product listing endpoints"""

    products: list[ProductListItem]
    pagination: PaginationInfo


# Query parameter schemas
class ProductSortBy(str, Enum):
    CREATED_AT = "created_at"
    PRICE = "price"
    NAME = "name"


class SortOrder(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class ProductListFilters(BaseModel):
    """Query parameters for filtering product lists"""

    category_id: Optional[int] = Field(None, description="Filter by category")
    tag_ids: Optional[list[int]] = Field(None, description="Filter by tag IDs")
    sort_by: ProductSortBy = Field(ProductSortBy.CREATED_AT, description="Sort field")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Sort order")
