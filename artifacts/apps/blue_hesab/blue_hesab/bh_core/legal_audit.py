from __future__ import annotations

import json
import os
import traceback
from typing import Any, Dict, Optional

import frappe
from frappe.utils import now


def _dirpath() -> str:
    return frappe.get_site_path("private", "files", "bh_regress")


def append_line(filename: str, payload: Dict[str, Any]) -> Optional[str]:
    try:
        d = _dirpath()
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, filename)
        row: Dict[str, Any] = {
            "ts": now(),
            "site": getattr(frappe.local, "site", None),
            "user": getattr(getattr(frappe, "session", None), "user", None),
        }
        row.update(payload or {})
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return path
    except Exception:
        try:
            frappe.log_error(traceback.format_exc(), "BH Legal Audit: append_line failed")
        except Exception:
            pass
        return None


def log_tamper(action: str, *, name: str, details: Optional[Dict[str, Any]] = None) -> None:
    payload = {"action": action, "doctype": "BH Legal Output", "name": name}
    if details:
        payload["details"] = details
    append_line("legal_tamper.log", payload)


def log_chain(action: str, *, ref_doctype: str, ref_name: str, out_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> None:
    payload = {"action": action, "ref_doctype": ref_doctype, "ref_name": ref_name, "out_name": out_name}
    if details:
        payload["details"] = details
    append_line("legal_chain.log", payload)


def log_policy(action: str, *, details: Optional[Dict[str, Any]] = None) -> None:
    payload = {"action": action}
    if details:
        payload["details"] = details
    append_line("legal_policy.log", payload)
