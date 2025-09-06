from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .api.v1.router import api_router as api_v1_router
from .core.config import settings
from .core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up Maxi'Mousse...")

    # Test database connection on startup
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Database connection successful: {result.scalar()}")
    except Exception as e:
        print(f"Database connection failed: {e}")

    yield
    print("Shutting down Maxi'Mousse...")


# Create FastAPI app with modern lifespan handler
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="E-commerce API for Maxi'Mousse products with multilingual support",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    api_v1_router,
    prefix=settings.API_V1_STR,
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}
