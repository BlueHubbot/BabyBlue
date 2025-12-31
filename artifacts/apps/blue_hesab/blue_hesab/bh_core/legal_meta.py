from __future__ import annotations

import os
from contextlib import contextmanager

import frappe

# LEGAL schema and generator build identifiers (auditable + reproducible)
DEFAULT_SCHEMA_VERSION = os.environ.get("BH_LEGAL_SCHEMA_VERSION", "LEGAL-V1")
DEFAULT_GENERATOR_BUILD = os.environ.get("BH_LEGAL_GENERATOR_BUILD", "BH-DEV")


def get_schema_version(explicit: str | None = None) -> str:
    return (explicit or DEFAULT_SCHEMA_VERSION).strip()


def get_generator_build(explicit: str | None = None) -> str:
    return (explicit or DEFAULT_GENERATOR_BUILD).strip()


def get_git_head_short() -> str | None:
    try:
        # best-effort: works if bench is a git clone
        from subprocess import check_output  # nosec

        out = check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=frappe.get_app_path("blue_hesab"),
        )  # nosec
        return out.decode("utf-8", "ignore").strip() or None
    except Exception:
        return None


def _set_db_emit_flag(on: bool) -> None:
    """Session-scoped DB flag for MariaDB triggers (policy lock)."""
    try:
        frappe.db.sql(f"SET @bh_legal_emit = {1 if on else 0}")
    except Exception:
        pass


@contextmanager
def legal_emit_scope():
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
        if n2 < 0:
            n2 = 0
        setattr(flags, "_bh_legal_emit_nesting", n2)

        if n2 == 0:
            _set_db_emit_flag(False)
            prev = bool(getattr(flags, "_bh_legal_emit_prev", False))
            flags.bh_legal_emit = prev
            try:
                delattr(flags, "_bh_legal_emit_prev")
            except Exception:
                pass
