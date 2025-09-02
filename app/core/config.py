from typing import Optional
from urllib.parse import quote_plus

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
        "validate_assignment": True,
    }

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Maxi'Mousse API"
    API_HOST: str = Field(default="0.0.0.0", description="API host address")
    API_PORT: int = Field(default=8000, ge=1, le=65535, description="API port number")
    API_DEBUG: bool = Field(default=False, description="Enable debug mode")

    # Environment
    ENVIRONMENT: str = Field(
        default="development", description="Application environment"
    )
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Database
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=5432, ge=1, le=65535, description="Database port")
    DB_NAME: str = Field(default="chocomax", description="Database name")
    DB_USER: str = Field(default="postgres", description="Database username")
    DB_PASSWORD: str = Field(
        default="your_secure_password_here", description="Database password"
    )
    DB_SCHEMA: str = Field(default="public", description="Database schema")
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="Complete database URL (overrides individual DB settings)",
    )

    @computed_field
    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        encoded_password = quote_plus(self.DB_PASSWORD)
        base_url = (
            f"postgresql+asyncpg://{self.DB_USER}:{encoded_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        return base_url


settings = Settings()
