from __future__ import annotations

from pathlib import Path
import subprocess
import datetime as _dt


def _app_root() -> Path:
    # .../apps/blue_hesab/blue_hesab/bh_core/legal_meta.py -> parents[2] == .../apps/blue_hesab
    return Path(__file__).resolve().parents[2]


def get_schema_version(default: str = "BH-DEV") -> str:
    p = _app_root() / "VERSION"
    try:
        v = p.read_text(encoding="utf-8").strip()
        return v or default
    except Exception:
        return default


def get_git_head_short() -> str | None:
    root = _app_root()
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(root),
            stderr=subprocess.DEVNULL,
        )
        s = out.decode("utf-8", "ignore").strip()
        return s or None
    except Exception:
        return None


def get_generator_build() -> str:
    sv = get_schema_version()
    head = get_git_head_short()
    return f"{sv}@{head}" if head else sv

def get_legal_meta(*, schema_version: str | None = None, generator_build: str | None = None) -> dict:
    """
    LEGAL meta helper used by legal_output.create_legal_output
    Returns: {schema_version, generator_build, generated_at}
    """
    sv = (schema_version or "").strip() or get_schema_version()
    if generator_build and str(generator_build).strip():
        gb = str(generator_build).strip()
    else:
        head = get_git_head_short()
        gb = f"{sv}@{head}" if head else sv

    return {
        "schema_version": sv,
        "generator_build": gb,
        "generated_at": str(_dt.datetime.utcnow()),
    }
