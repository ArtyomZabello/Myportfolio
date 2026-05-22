"""HTTP header helpers for authenticated Conduit API requests."""


def authorization_headers(token: str) -> dict[str, str]:
    """Build RealWorld Authorization headers for authenticated API requests."""
    return {"Authorization": f"Token {token}"}
