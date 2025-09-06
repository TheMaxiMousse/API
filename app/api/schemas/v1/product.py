from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

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


class ProductAttributeInput(BaseModel):
    """Schema for product attribute input"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Attribute name (e.g., 'allergen')",
    )
    value: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Attribute value (e.g., 'gluten')",
    )
    color: Optional[str] = Field(
        None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color (e.g., '#FF6B6B')"
    )


class ProductTranslationInput(BaseModel):
    """Schema for product translation input"""

    language_iso: str = Field(
        ..., pattern=r"^[a-z]{2}$", description="Language ISO code"
    )
    name: str = Field(
        ..., min_length=3, max_length=200, description="Translated product name"
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="Translated description"
    )


class CreateProductRequest(BaseModel):
    """Request schema for creating a new product"""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Required fields
    product_name: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Product name",
        pattern=r"^[^<>\'\"]+$",  # Prevent XSS characters
    )
    product_description: str = Field(
        ..., min_length=1, max_length=2000, description="Product description"
    )
    product_type: ProductType = Field(..., description="Type of product")
    category_id: int = Field(..., ge=1, description="Category ID")

    # Pricing (conditional based on product_type)
    price: Optional[Decimal] = Field(
        None, ge=0, le=999999.99, description="Price for standard/variant products"
    )
    base_price: Optional[Decimal] = Field(
        None, ge=0, le=999999.99, description="Base price for configurable products"
    )

    # Optional fields
    image_url: Optional[str] = Field(
        None,
        pattern=r"^https?://[^\s]+\.(jpg|jpeg|png|webp)(\?[^\s]*)?$",
        description="Product image URL",
    )
    preparation_time_hours: int = Field(
        48, ge=0, le=24 * 365, description="Preparation time in hours"
    )
    min_order_hours: int = Field(
        48, ge=0, le=24 * 365, description="Minimum order advance time in hours"
    )
    serving_info: Optional[str] = Field(
        None, max_length=200, description="Serving information (e.g., '4-6 persons')"
    )
    is_customizable: bool = Field(False, description="Whether product is customizable")

    # Related data
    tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs to assign")
    attributes: Optional[List[ProductAttributeInput]] = Field(
        None, description="Product attributes"
    )
    translations: Optional[List[ProductTranslationInput]] = Field(
        None, description="Product translations"
    )

    @model_validator(mode="after")
    def validate_pricing(self) -> "CreateProductRequest":
        """Validate pricing based on product type"""
        if self.product_type == ProductType.CONFIGURABLE:
            if self.base_price is None:
                raise ValueError("Configurable products require a base_price")
            if self.price is not None:
                # Clear price for configurable products
                self.price = None
        else:
            if self.price is None:
                raise ValueError("Standard and variant-based products require a price")
            if self.base_price is not None:
                # Clear base_price for non-configurable products
                self.base_price = None
        return self


class CreateProductResponse(BaseModel):
    """Response schema for product creation"""

    model_config = ConfigDict(from_attributes=True)

    product_id: int = Field(..., description="Created product ID")
    product_name: str = Field(..., description="Product name")
    message: str = Field(..., description="Success message")
    created_at: datetime = Field(..., description="Timestamp of creation")
