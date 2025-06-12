"""
Email utility package initialization.

This module exposes the main email configuration, schemas, and sending functions
for use throughout the application. Import from this module to access email-related
utilities in a unified manner.
"""

from .config import EmailConfig
from .schemas import RegistrationEmailSchema
from .sender import send_email_background
