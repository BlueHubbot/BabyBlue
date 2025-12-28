# apps/blue_hesab/blue_hesab/bh_core/vat_ci_v15.py
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Iterable

import frappe


def _safe_sp_name(prefix: str = "bhvat15") -> str:
    h = getattr(frappe, "generate_hash", None)
    suffix = h(length=6) if callable(h) else str(int(time.time()))[-6:]
    raw = f"{prefix}_{int(time.time())}_{suffix}"
    # MariaDB-safe: letters/digits/underscore only
    return re.sub(r"[^0-9A-Za-z_]+", "_", raw)


def _rollback_to_savepoint(sp: str) -> None:
    try:
        # Frappe Database.rollback(save_point=...)
        frappe.db.rollback(save_point=sp)  # type: ignore[arg-type]
        return
    except TypeError:
        pass
    except Exception:
        pass

    # hard fallback
    try:
        frappe.db.sql(f"ROLLBACK TO SAVEPOINT `{sp}`")
    except Exception:
        # last resort
        frappe.db.rollback()


def _resolve_report_abs(site: str, report_value: Any) -> Path | None:
    if not report_value:
        return None

    s = str(report_value)
    p = Path(s)
    if p.is_absolute() and p.exists():
        return p

    # most common: ".../private/files/<REL>"
    marker = "/private/files/"
    if marker in s:
        rel = s.split(marker, 1)[1]
        base = Path(frappe.get_site_path("private", "files"))
        return base / rel

    marker2 = "private/files/"
    if marker2 in s:
        rel = s.split(marker2, 1)[1]
        base = Path(frappe.get_site_path("private", "files"))
        return base / rel

    # treat as relative to site path
    try:
        return Path(frappe.get_site_path()) / s
    except Exception:
        return None


def _iter_docnames(report_json: dict) -> Iterable[tuple[str, str]]:
    """
    yields: (doctype, name)
    expects rows shape used by your regress scripts:
      purchase row: {"pi": "<name>", ...}
      sales row: {"si": "<name>", ...}
    """
    try:
        p_rows = ((report_json.get("purchase") or {}).get("rows") or [])
        for r in p_rows:
            name = (r or {}).get("pi") or (r or {}).get("name")
            if name:
                yield ("Purchase Invoice", str(name))
    except Exception:
        pass

    try:
        s_rows = ((report_json.get("sales") or {}).get("rows") or [])
        for r in s_rows:
            name = (r or {}).get("si") or (r or {}).get("name")
            if name:
                yield ("Sales Invoice", str(name))
    except Exception:
        pass


@frappe.whitelist()
def run_ep01_v03_cli_v15(rate: int = 1000000, site: str | None = None) -> dict:
    """
    VAT-15:
      - Run existing BH-EP01 v0.3 CI (vat_ci.run_ep01_v03_cli)
      - Ensure DB cleanup via SAVEPOINT + ROLLBACK
      - Verify no created Sales/Purchase Invoices remain in DB

    + VAT-10 scope regress:
      - If BH Settings.default_company is set:
          * enforce must be True for default_company
          * enforce must be False for any other company string

    Returns a small summary dict (and keeps the original report JSON file on disk).
    """
    site_name = site or frappe.local.site or "baba.bluehesab.ir"

    from blue_hesab.bh_core import vat_ci
    from blue_hesab.bh_core.vat_pipeline import _bh_vat_enforced

    # --- VAT-10 scope check (regress guard) ---
    vat10_scope = {"default_company": None, "enforced_default": None, "enforced_other": None, "ok": True}
    try:
        s = frappe.get_single("BH Settings")
        dc = (getattr(s, "default_company", None) or "").strip()
        vat10_scope["default_company"] = dc or None

        print("\n=== VAT-10 SCOPE CHECK ===")
        if dc:
            enforced_default = bool(_bh_vat_enforced(company=dc))
            enforced_other = bool(_bh_vat_enforced(company="__NOT_DEFAULT__"))

            vat10_scope["enforced_default"] = enforced_default
            vat10_scope["enforced_other"] = enforced_other
            vat10_scope["ok"] = bool(enforced_default is True and enforced_other is False)

            print("default_company:", dc)
            print("enforced_default:", enforced_default)
            print("enforced_other:", enforced_other)

            if not vat10_scope["ok"]:
                raise Exception(
                    f"VAT-10 scope FAIL: default_company={dc} enforced_default={enforced_default} enforced_other={enforced_other}"
                )
        else:
            print("SKIP (BH Settings.default_company is empty)")
    except Exception:
        vat10_scope["ok"] = False
        raise

    sp = _safe_sp_name()
    frappe.db.savepoint(sp)

    base_out: dict = {}
    report_abs: Path | None = None
    created: list[tuple[str, str]] = []
    leftovers: list[tuple[str, str]] = []

    try:
        base_out = vat_ci.run_ep01_v03_cli(rate=rate) or {}
        report_abs = _resolve_report_abs(site_name, base_out.get("report"))

        # read report rows (for docnames) BEFORE rollback (file is on disk anyway)
        if report_abs and report_abs.exists():
            try:
                payload = json.loads(report_abs.read_text(encoding="utf-8"))
                created = list(_iter_docnames(payload))
            except Exception:
                created = []

    finally:
        _rollback_to_savepoint(sp)

    # Verify cleanup
    for dt, name in created:
        try:
            if frappe.db.exists(dt, name):
                leftovers.append((dt, name))
        except Exception:
            # conservative: if exists check fails, treat as leftover unknown
            leftovers.append((dt, name))

    cleanup_ok = (len(leftovers) == 0)

    out = {
        "vat10_scope": vat10_scope,
        "vat15": {
            "sp": sp,
            "created_docs": len(created),
            "cleanup_ok": cleanup_ok,
            "leftovers": leftovers[:50],  # cap
        },
        "base_ok": bool(base_out.get("ok")),
        "ok": bool(base_out.get("ok")) and cleanup_ok and bool(vat10_scope.get("ok")),
        "report": base_out.get("report"),
        "intent": base_out.get("intent"),
        "purchase": base_out.get("purchase"),
        "sales": base_out.get("sales"),
    }

    print("\n=== VAT-15 CLEAN CI (SAVEPOINT) ===")
    print("VAT-10 Scope OK:", bool(vat10_scope.get("ok")))
    print("Base CI OK:", out["base_ok"])
    print("Created docs:", out["vat15"]["created_docs"])
    print("Cleanup OK:", cleanup_ok)
    if not cleanup_ok:
        print("Leftovers (first 50):", out["vat15"]["leftovers"])

    if not out["ok"]:
        raise Exception("VAT FAIL: VAT-10 scope OR base CI OR cleanup failed. See output + report JSON.")

    return out
