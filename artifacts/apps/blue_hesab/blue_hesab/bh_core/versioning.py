# apps/blue_hesab/blue_hesab/bh_core/versioning.py
from __future__ import annotations

from pathlib import Path

def get_schema_version() -> str:
    """
    Single source of truth for schema_version.
    Priority:
      1) blue_hesab/__init__.__version__
      2) apps/blue_hesab/VERSION file (your GitOps tag)
      3) fallback: DEV
    """
    # 1) package version
    try:
        from blue_hesab import __version__  # type: ignore
        if __version__:
            return str(__version__)
    except Exception:
        pass

    # 2) VERSION file (preferred in your setup)
    try:
        import frappe  # local bench env
        app_pkg_path = Path(frappe.get_app_path("blue_hesab"))  # .../apps/blue_hesab/blue_hesab
        app_root = app_pkg_path.parent  # .../apps/blue_hesab
        ver_file = app_root / "VERSION"
        if ver_file.exists():
            v = ver_file.read_text(encoding="utf-8").strip()
            if v:
                return v
    except Exception:
        pass

    return "DEV"
