"""
This is the main entry point for the API application.
It sets up the FastAPI application, includes the home router, and mounts versioned APIs.
"""

from fastapi import FastAPI
from routes.home import router as home_router
from routes.v1 import api as v1
from routes.v2 import api as v2

__version__ = "0.1.0"  # TODO: Update this version with GitHub Actions

app = FastAPI(title="ChocoMax Shop API")

# Home (non-versioned)
app.include_router(home_router)

# Versioned API
app.mount("/api/v1", v1)
app.mount("/api/v2", v2)


def main():
    """
    Main function to run the FastAPI application.
    This is typically used when running the app with a command like `python main.py`.
    """
    import uvicorn

    uvicorn.run("main:app", reload=True)


if __name__ == "__main__":
    main()
