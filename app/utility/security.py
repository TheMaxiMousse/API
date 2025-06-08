import base64
import hashlib
import os

from argon2 import PasswordHasher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ph = PasswordHasher()

AES_KEY = bytes.fromhex(os.getenv("AES_SECRET_KEY", os.urandom(32).hex()))
PEPPER = os.getenv("PEPPER", "SuperSecretPepper").encode("utf-8")


def normalize_email(email: str) -> str:
    """Normalize email by stripping spaces and converting to lowercase."""
    return email.strip().lower()


def normalize_phone(phone: str) -> str:
    """Normalize phone number by stripping spaces and removing non-numeric characters."""
    return phone.strip().replace(" ", "")


def encrypt_field(value: str) -> str:
    """Encrypt a value using AES-256-GCM (returns base64 of IV + ciphertext + tag)."""
    aesgcm = AESGCM(AES_KEY)
    iv = os.urandom(12)  # 96-bit IV recommended for AES-GCM
    ciphertext = aesgcm.encrypt(iv, value.encode("utf-8"), associated_data=None)
    return base64.b64encode(iv + ciphertext).decode("utf-8")


def decrypt_field(encrypted_base64: str) -> str:
    """Decrypt a value encrypted with AES-256-GCM."""
    encrypted_data = base64.b64decode(encrypted_base64)
    iv, ciphertext = encrypted_data[:12], encrypted_data[12:]
    aesgcm = AESGCM(AES_KEY)
    decrypted = aesgcm.decrypt(iv, ciphertext, associated_data=None)
    return decrypted.decode("utf-8")


def hash_field(value: str) -> str:
    """Generate a SHA-256 hash of a field (used for fast lookup)."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    """Hash a password using Argon2 + pepper."""
    peppered_password = password.encode("utf-8") + PEPPER
    return ph.hash(peppered_password)


# Wrappers for email and phone to ensure normalization and hashing


def hash_email(email: str) -> str:
    """Generate a SHA-256 hash of the email (used for fast lookup)."""
    return hash_field(normalize_email(email))


def hash_phone(phone: str) -> str:
    """Generate a SHA-256 hash of the phone number (used for fast lookup)."""
    return hash_field(normalize_phone(phone))


def encrypt_email(email: str) -> str:
    """Encrypt the email after normalizing it."""
    return encrypt_field(normalize_email(email))


def encrypt_phone(phone: str) -> str:
    """Encrypt the phone number after normalizing it."""
    return encrypt_field(normalize_phone(phone))
