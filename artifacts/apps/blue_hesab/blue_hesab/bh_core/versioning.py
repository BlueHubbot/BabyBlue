# apps/blue_hesab/blue_hesab/bh_core/versioning.py
from __future__ import annotations

import os
from pathlib import Path


def _read_version_file() -> str | None:
    try:
        import frappe
        app_pkg_path = Path(frappe.get_app_path("blue_hesab"))  # .../apps/blue_hesab/blue_hesab
        app_root = app_pkg_path.parent  # .../apps/blue_hesab
        ver_file = app_root / "VERSION"
        if ver_file.exists():
            v = ver_file.read_text(encoding="utf-8").strip()
            return v or None
    except Exception:
        return None
    return None


def get_schema_version() -> str:
    """
    Single source of truth for schema_version.

    Per Master Spec:
      schema_version MUST be Git Tag (BH-YYYYMMDD.N) stored in apps/blue_hesab/VERSION.
    """
    # 1) VERSION file (authoritative in your GitOps)
    v = _read_version_file()
    if v:
        return v

    # 2) fallback: package __version__ (optional)
    try:
        from blue_hesab import __version__  # type: ignore
        v2 = str(__version__ or "").strip()
        if v2:
            return v2
    except Exception:
        pass

    return "DEV"


def get_generator_build() -> str:
    """
    Build identifier for audit (generator_build).
    Default: generator_build == schema_version (tag).
    Optional override via env for emergency debugging.
    """
    v = (
        os.environ.get("BH_GENERATOR_BUILD")
        or os.environ.get("BH_LEGAL_GENERATOR_BUILD")
        or os.environ.get("GENERATOR_BUILD")
    )
    if v and str(v).strip():
        return str(v).strip()

    return get_schema_version()
