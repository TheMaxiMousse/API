from fastapi import APIRouter

from .endpoints import products

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(products.router, prefix="/products", tags=["products"])
