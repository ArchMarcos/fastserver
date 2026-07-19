"""PortunusDB Python SDK.

A minimal, zero-dependency client for PortunusDB.

Usage::

    from portunus import Client

    db = Client("http://127.0.0.1:3100", user="root", password="<sua-senha-aqui>")
    db.use("app", "users")
    db.create(name="Alice", age=30)
"""

from .client import Client
from .errors import (
    PortunusError,
    AuthError,
    NotFoundError,
    PermissionError,
    ConnectionError,
)

__all__ = [
    "Client",
    "PortunusError",
    "AuthError",
    "NotFoundError",
    "PermissionError",
    "ConnectionError",
]

__version__ = "0.1.0"