"""
This module exposes user-related request schemas.

It imports and re-exports the UserLogin, UserLogin2FA, and UserRegister schemas
for use in endpoint definitions.
"""

from .login import UserLogin, UserLogin2FA
from .register import UserRegister
