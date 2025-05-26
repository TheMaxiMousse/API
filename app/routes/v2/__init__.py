"""
Base module for the API version 2 routes.
"""

from fastapi import FastAPI

__version__ = "2.0.0"

api = FastAPI(title="ChocoMax Shop API", version=__version__)
