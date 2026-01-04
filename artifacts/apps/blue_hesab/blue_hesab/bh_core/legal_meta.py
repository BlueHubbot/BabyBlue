from __future__ import annotations

import os
from contextlib import contextmanager

import frappe

from . import versioning as _bh_ver

# LEGAL schema and generator build identifiers (auditable + reproducible)
# IMPORTANT: schema_version must follow Git tag policy (apps/blue_hesab/VERSION).
DEFAULT_SCHEMA_VERSION = _bh_ver.get_schema_version()
DEFAULT_GENERATOR_BUILD = _bh_ver.get_generator_build()


def get_schema_version(explicit: str | None = None) -> str:
    return (explicit or DEFAULT_SCHEMA_VERSION).strip()


def get_generator_build(explicit: str | None = None) -> str:
    return (explicit or DEFAULT_GENERATOR_BUILD).strip()


def _set_db_emit_flag(enabled: bool) -> None:
    """
    DB session var used by DB triggers:
      @bh_legal_emit = 1 allows insert/update in BH Legal Output.
    """
    try:
        frappe.db.sql("SET @bh_legal_emit = %s", (1 if enabled else 0,))
    except Exception:
        # during tests some contexts may not have DB ready
        pass


@contextmanager
def allow_legal_emit():
    """Allow creating BH Legal Output only inside this scope.

    - Python-level guard: frappe.flags.bh_legal_emit
    - DB-level guard: @bh_legal_emit (used by BEFORE INSERT trigger)
    - Supports nesting safely.
    """
    flags = frappe.flags
    n = int(getattr(flags, "_bh_legal_emit_nesting", 0) or 0)

    if n == 0:
        # store previous state (avoid leaking bh_legal_emit=True into later code)
        setattr(flags, "_bh_legal_emit_prev", bool(getattr(flags, "bh_legal_emit", False)))
        flags.bh_legal_emit = True
        _set_db_emit_flag(True)

    setattr(flags, "_bh_legal_emit_nesting", n + 1)
    try:
        yield
    finally:
        # unwind nesting
        n2 = int(getattr(flags, "_bh_legal_emit_nesting", 1) or 1) - 1
        setattr(flags, "_bh_legal_emit_nesting", n2)

        if n2 <= 0:
            # restore previous state
            prev = bool(getattr(flags, "_bh_legal_emit_prev", False))
            flags.bh_legal_emit = prev
            _set_db_emit_flag(False)

# --- Backward-compatible alias (regress suites import this name) ---
def legal_emit_scope():
    return allow_legal_emit()
