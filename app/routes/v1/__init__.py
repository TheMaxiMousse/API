# routes/v1/__init__.py

from fastapi import FastAPI

from .orders import router as order_router
from .products import router as product_router

__version__ = "1.0.0"

api = FastAPI(title=f"ChocoMax Shop API", version=__version__)

api.include_router(product_router, prefix="/products", tags=["Products"])
api.include_router(order_router, prefix="/orders", tags=["Orders"])
