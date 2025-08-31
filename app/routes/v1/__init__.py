"""
Base module for the API version 1 routes.
"""

from fastapi import FastAPI

from .endpoints.products import router as product_router

__version__ = "1.2.0"

api = FastAPI(title="ChocoMax Shop API", version=__version__)

api.include_router(product_router, prefix="/products", tags=["Products"])
