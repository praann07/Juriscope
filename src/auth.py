import base64
import os
import secrets
from typing import Optional, Tuple


def get_login_credentials() -> Optional[Tuple[str, str]]:
    """Return (username, password) from the environment, or None if login is off.

    Login is only enforced when both JURISCOPE_USERNAME and JURISCOPE_PASSWORD are
    set, so local development keeps working without extra setup.
    """
    username = os.getenv("JURISCOPE_USERNAME")
    password = os.getenv("JURISCOPE_PASSWORD")
    if username and password:
        return username, password
    return None


def is_authorized(authorization_header: Optional[str], username: str, password: str) -> bool:
    """Check an HTTP Basic Authorization header against the expected credentials."""
    if not authorization_header or not authorization_header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(authorization_header[len("Basic "):].strip()).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return False

    given_user, separator, given_password = decoded.partition(":")
    if not separator:
        return False

    # Compare in constant time so the check does not leak how much of a guess was right.
    user_ok = secrets.compare_digest(given_user.encode("utf-8"), username.encode("utf-8"))
    password_ok = secrets.compare_digest(given_password.encode("utf-8"), password.encode("utf-8"))
    return user_ok and password_ok
