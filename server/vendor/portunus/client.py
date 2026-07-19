"""PortunusDB Python SDK — Client class.

Dependencies: Python 3.10+ stdlib only (urllib).
"""

from __future__ import annotations
import json
import urllib.request
import urllib.error
from typing import Any

from .errors import PortunusError, ConnectionError, from_api_message
from . import utils
from . import msgpack


class Client:
    """Synchronous client for the PortunusDB HTTP API.

    Usage::

        # Auto-login with password
        db = Client("http://127.0.0.1:3100", user="root", password="<sua-senha-aqui>")
        db.use("app", "users")
        db.create(nome="Alice", idade=30)

        # Or provide a pre-existing token
        db = Client("http://127.0.0.1:3100", user="root", token="uuid")
    """

    def __init__(
        self,
        url: str = "http://127.0.0.1:3100",
        *,
        user: str,
        token: str | None = None,
        password: str | None = None,
        database: str | None = None,
        table: str | None = None,
        timeout: float = 30,
    ):
        self._url = url.rstrip("/")
        self._user = user
        self._token = token
        self._database = database or "."
        self._table = table or "."
        self._timeout = timeout

        if not self._token and not password:
            raise ValueError("Provide either 'token' or 'password'")
        if not self._token:
            self._login(password)

    # ──────────────────────────────────────────────
    #  HTTP internals
    # ──────────────────────────────────────────────

    def _post(self, path: str, payload: dict) -> dict:
        """POST JSON and return decoded response dict."""
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{self._url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read()
        except urllib.error.URLError as exc:
            raise ConnectionError(f"Cannot reach {self._url}: {exc}") from exc

        # /health always returns JSON; /login and /execute return MessagePack.
        if raw and raw[0:1] in (b"{", b"["):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"success": False, "error": f"invalid response: {raw!r}"}
        try:
            return msgpack.loads(raw)
        except ValueError:
            return {"success": False, "error": f"invalid response: {raw!r}"}

    def _login(self, password: str) -> None:
        """Authenticate with username/password and store the token."""
        resp = self._post("/login", {"user": self._user, "password": password})
        if not resp.get("success"):
            raise from_api_message(resp.get("error", "login failed"))
        token = resp.get("data", {}).get("token")
        if not token:
            raise PortunusError("login succeeded but no token returned")
        self._token = token

    def _execute(self, script: str, *, database: str | None = None, table: str | None = None) -> Any:
        """Send a PortunusQL script to /execute and return ``data`` on success."""
        payload = {
            "user": self._user,
            "token": self._token,
            "database": database or self._database,
            "table": table or self._table,
            "script": script,
        }
        resp = self._post("/execute", payload)
        if not resp.get("success"):
            raise from_api_message(resp.get("error", "unknown error"))
        return resp.get("data")

    def _exec_ctx(self, script: str, *, database: str | None = None, table: str | None = None) -> Any:
        """Execute a script with explicit db/table context override, raise on error."""
        return self._execute(script, database=database, table=table)

    # ──────────────────────────────────────────────
    #  Context management
    # ──────────────────────────────────────────────

    def use(self, database: str, table: str | None = None) -> "Client":
        """Select active database (and optionally table). Returns self for chaining."""
        self._database = database
        self._table = table or self._table
        return self

    # ──────────────────────────────────────────────
    #  Database-level commands
    # ──────────────────────────────────────────────

    def create_database(self, name: str) -> dict:
        return self._exec_ctx(f"CREATE DATABASE {name}", database=".", table=".")

    def drop_database(self, name: str) -> dict:
        return self._exec_ctx(f"DROP DATABASE {name}", database=".", table=".")

    def list_databases(self) -> list:
        return self._exec_ctx("LIST DATABASES", database=".", table=".")

    def status_database(self, name: str) -> dict:
        return self._exec_ctx(f"STATUS DATABASE {name}", database=".", table=".")

    # ──────────────────────────────────────────────
    #  Table-level commands
    # ──────────────────────────────────────────────

    def create_table(self, name: str) -> dict:
        return self._exec_ctx(f"CREATE TABLE {name}", table=".")

    def drop_table(self, name: str) -> dict:
        return self._exec_ctx(f"DROP TABLE {name}", table=".")

    def list_tables(self) -> list:
        return self._exec_ctx("LIST TABLES", table=".")

    def describe_table(self, name: str) -> dict:
        return self._exec_ctx(f"DESCRIBE TABLE {name}", table=".")

    # ──────────────────────────────────────────────
    #  CRUD
    # ──────────────────────────────────────────────

    def create(self, **fields: Any) -> dict:
        """Insert a record. Returns the created record."""
        return self._execute(utils.build_create(**fields))

    def get(self, *args, **filters: Any) -> Any:
        """Fetch by id (positional) or by field filters.

        - ``get(1)``          → single record dict
        - ``get(nome="Alice")`` → list of matching records
        """
        return self._execute(utils.build_get(*args, **filters))

    def list(self, limit: int | None = None, offset: int | None = None) -> list:
        """List records with optional pagination."""
        return self._execute(utils.build_list(limit, offset))

    def update(self, updates: dict, **where: Any) -> Any:
        """Update records matching WHERE."""
        return self._execute(utils.build_update(updates, **where))

    def delete(self, **where: Any) -> Any:
        """Delete records matching filter."""
        return self._execute(utils.build_delete(**where))

    # ──────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────

    def find(self, *, limit: int | None = None, **where: Any) -> list:
        """Find records matching WHERE (optional LIMIT)."""
        return self._execute(utils.build_find(limit, **where))

    def exists(self, **where: Any) -> bool:
        """Return True/False whether any record matches."""
        data = self._execute(utils.build_exists(**where))
        if isinstance(data, dict):
            return bool(data.get("exists", False))
        return bool(data)

    def count(self, **where: Any) -> int:
        """Return number of records (optionally filtered)."""
        data = self._execute(utils.build_count(**where))
        if isinstance(data, dict):
            return int(data.get("count", 0))
        return int(data)

    def first(self, **where: Any) -> dict:
        """Return the first matching record or raise."""
        return self._execute(utils.build_first(**where))

    # ──────────────────────────────────────────────
    #  Migration & Maintenance
    # ──────────────────────────────────────────────

    def migrate(self, table: str | None = None, **defaults: Any) -> dict:
        return self._execute(utils.build_migrate(table, **defaults))

    def backup(self) -> dict:
        return self._exec_ctx("BACKUP", table=".")

    def check(self) -> dict:
        return self._exec_ctx("CHECK", table=".")

    # ──────────────────────────────────────────────
    #  Indexes
    # ──────────────────────────────────────────────

    def create_index(self, field: str) -> dict:
        return self._execute(f"CREATE INDEX {field}")

    def drop_index(self, field: str) -> dict:
        return self._execute(f"DROP INDEX {field}")

    def list_indexes(self) -> list:
        return self._execute("LIST INDEXES")

    # ──────────────────────────────────────────────
    #  Raw access (escape hatch)
    # ──────────────────────────────────────────────

    def raw(self, script: str, *, database: str | None = None, table: str | None = None) -> Any:
        """Execute an arbitrary PortunusQL script string. Use for unsupported commands."""
        return self._execute(script, database=database, table=table)

    # ──────────────────────────────────────────────
    #  Health
    # ──────────────────────────────────────────────

    def health(self) -> dict:
        """Check server health via GET /health."""
        req = urllib.request.Request(f"{self._url}/health")
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read()
        except urllib.error.URLError as exc:
            raise ConnectionError(f"Cannot reach {self._url}: {exc}") from exc
        if raw and raw[0:1] in (b"{", b"["):
            return json.loads(raw)
        return msgpack.loads(raw)