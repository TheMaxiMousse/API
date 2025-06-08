"""
This module initializes the SQLAlchemy declarative base for all ORM models.

All model classes should inherit from `Base` to ensure proper table mapping.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
