import re


def sanitize_username(username: str) -> str:
    """
    Replace all characters not allowed by the database username constraint
    (^[a-zA-Z0-9_]+$) with underscores.
    """
    return re.sub(r"[^a-zA-Z0-9_]", "_", username)
