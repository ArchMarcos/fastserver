"""Portunus SDK exceptions."""


class PortunusError(Exception):
    """Generic error returned by the PortunusDB API (success=false)."""


class AuthError(PortunusError):
    """Authentication failure — invalid credentials or token."""


class NotFoundError(PortunusError):
    """Resource not found — database, table, or record."""


class PermissionError(PortunusError):
    """Role lacks permission for the requested action."""


class ConnectionError(PortunusError):
    """Unable to reach the server."""


def from_api_message(msg: str) -> PortunusError:
    """Map an API error message string to the most specific exception."""
    low = msg.lower()
    if low.startswith("authentication failed"):
        return AuthError(msg)
    if low.startswith("not found"):
        return NotFoundError(msg)
    if low.startswith("permission denied"):
        return PermissionError(msg)
    return PortunusError(msg)