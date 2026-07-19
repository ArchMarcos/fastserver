"""Pure helpers for building PortunusQL scripts and escaping values."""

from __future__ import annotations
from typing import Any


def escape_value(val: Any) -> str:
    """Return a safe DSL literal representation of a Python value.

    - bool  → true / false
    - int   → 42
    - float → 3.14
    - str   → 'text' (single-quoted, internal quotes escaped)
    """
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return repr(val)
    if isinstance(val, str):
        escaped = val.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"
    if val is None:
        return "''"
    raise TypeError(f"Unsupported value type for PortunusQL: {type(val).__name__}")


def build_kv(**fields: Any) -> str:
    """Build ``key='value' key2=123`` string from kwargs."""
    return " ".join(f"{k}={escape_value(v)}" for k, v in fields.items())


def build_where_clause(**filters: Any) -> str:
    """Build the condition part (without the WHERE keyword)."""
    return build_kv(**filters)


def build_create(**fields: Any) -> str:
    """Build a CREATE script string."""
    if not fields:
        raise ValueError("CREATE requires at least one key=value pair")
    return f"CREATE {build_kv(**fields)}"


def build_get(*args: Any, **filters: Any) -> str:
    """Build a GET script string.

    - ``get(1)``           → ``GET id=1``
    - ``get(name='Alice')`` → ``GET name='Alice'``
    """
    if args and filters:
        raise ValueError("GET accepts either a positional id or keyword filters, not both")
    if args:
        if len(args) > 1:
            raise ValueError("GET accepts at most one positional argument (id)")
        return f"GET id={escape_value(args[0])}"
    if not filters:
        raise ValueError("GET requires an id or field filters")
    return f"GET {build_kv(**filters)}"


def build_list(limit: int | None = None, offset: int | None = None) -> str:
    """Build a LIST script string with optional pagination."""
    parts = ["LIST"]
    if limit is not None:
        parts.append(f"LIMIT={limit}")
    if offset is not None:
        parts.append(f"OFFSET={offset}")
    return " ".join(parts)


def build_update(updates: dict, **where: Any) -> str:
    """Build an UPDATE script string."""
    if not updates:
        raise ValueError("UPDATE requires at least one field to update")
    if not where:
        raise ValueError("UPDATE requires a WHERE clause")
    set_clause = build_kv(**updates)
    where_clause = build_where_clause(**where)
    return f"UPDATE {set_clause} WHERE {where_clause}"


def build_delete(**where: Any) -> str:
    """Build a DELETE script string."""
    if not where:
        raise ValueError("DELETE requires a field filter")
    return f"DELETE {build_kv(**where)}"


def build_find(limit: int | None = None, **where: Any) -> str:
    """Build a FIND script string. LIMIT is a separate token (no =)."""
    if not where:
        raise ValueError("FIND requires a WHERE clause")
    script = f"FIND WHERE {build_where_clause(**where)}"
    if limit is not None:
        script += f" LIMIT {limit}"
    return script


def build_exists(**where: Any) -> str:
    """Build an EXISTS script string."""
    if not where:
        raise ValueError("EXISTS requires a field filter")
    return f"EXISTS {build_kv(**where)}"


def build_count(**where: Any) -> str:
    """Build a COUNT script string, optionally with WHERE."""
    if where:
        return f"COUNT WHERE {build_where_clause(**where)}"
    return "COUNT"


def build_first(**where: Any) -> str:
    """Build a FIRST script string."""
    if not where:
        raise ValueError("FIRST requires a field filter")
    return f"FIRST {build_kv(**where)}"


def build_migrate(table: str | None = None, **defaults: Any) -> str:
    """Build a MIGRATE script string."""
    if not defaults:
        raise ValueError("MIGRATE requires at least one field=default")
    if table:
        return f"MIGRATE TABLE {table} {build_kv(**defaults)}"
    return f"MIGRATE {build_kv(**defaults)}"