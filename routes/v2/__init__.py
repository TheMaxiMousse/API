# routes/v1/__init__.py

from fastapi import FastAPI

__version__ = "2.0.0"

api = FastAPI(title=f"ChocoMax Shop API", version=__version__)
