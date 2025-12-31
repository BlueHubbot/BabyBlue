from __future__ import annotations

import datetime as _dt
import json
import os
from typing import Any, Dict

import frappe
from frappe.model.document import Document

_POLICY_LOCK_MSG = "ثبت/ویرایش خروجی‌های قانونی فقط از مسیر رسمی BlueHesab مجاز است."
_IMMUTABLE_MSG = "خروجی قانونی پس از ثبت نهایی غیرقابل تغییر است."
_TAMPER_MSG = "خروجی قانونی دستکاری شده است. (عدم تطابق هش منبع/پیلود)"


def _append_log(filename: str, obj: Dict[str, Any]) -> None:
    try:
        base = frappe.get_site_path("private", "files", "bh_regress")
        os.makedirs(base, exist_ok=True)
        path = os.path.join(base, filename)
        payload = dict(obj)
        payload.setdefault("ts", str(_dt.datetime.utcnow()))
        payload.setdefault("site", frappe.local.site)
        payload.setdefault("user", getattr(frappe.session, "user", None))
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _emit_allowed() -> bool:
    """
    Official emit path sets `frappe.flags.bh_legal_emit = True`.
    """
    try:
        if bool(getattr(frappe.flags, "bh_legal_emit", False)):
            return True
        if bool(getattr(frappe.flags, "in_patch", False)) or bool(getattr(frappe.flags, "in_migrate", False)):
            return True
    except Exception:
        pass
    return False


class BHLegalOutput(Document):
    def validate(self):
        # Policy lock (UI/Frappe-path). DB triggers enforce SQL-path too.
        if not _emit_allowed():
            _append_log("legal_policy.log", {"action": "BLOCK_WRITE", "doctype": self.doctype, "name": self.name})
            frappe.throw(_POLICY_LOCK_MSG, frappe.ValidationError)

        # UI-level immutability (DB triggers enforce too)
        prev = None
        try:
            prev = self.get_doc_before_save()
        except Exception:
            prev = None

        if prev and int(getattr(prev, "docstatus", 0) or 0) == 1:
            immutable_fields = (
                "company",
                "output_type",
                "reference_doctype",
                "reference_name",
                "schema_version",
                "generator_build",
                "generated_by",
                "generated_at",
                "source_hash",
                "payload_hash",
                "source_json",
                "payload_json",
                "previous_output",
                "correction_reason",
            )
            for f in immutable_fields:
                if getattr(prev, f, None) != getattr(self, f, None):
                    _append_log(
                        "legal_policy.log",
                        {
                            "action": "BLOCK_IMMUTABLE_EDIT",
                            "name": self.name,
                            "field": f,
                            "before": getattr(prev, f, None),
                            "after": getattr(self, f, None),
                        },
                    )
                    frappe.throw(_IMMUTABLE_MSG, frappe.ValidationError)

        # tamper detection (best-effort): recompute hashes
        try:
            if int(getattr(self, "docstatus", 0) or 0) == 1:
                from blue_hesab.bh_core.legal_output import hash_obj

                src_json = getattr(self, "source_json", None)
                src_hash = getattr(self, "source_hash", None)
                if src_json and src_hash:
                    calc = hash_obj(json.loads(src_json))
                    if calc != src_hash:
                        _append_log("legal_tamper.log", {"action": "TAMPER_SOURCE", "name": self.name, "expected": src_hash, "got": calc})
                        frappe.throw(_TAMPER_MSG, frappe.ValidationError)

                pay_json = getattr(self, "payload_json", None)
                pay_hash = getattr(self, "payload_hash", None)
                if pay_json and pay_hash:
                    calc = hash_obj(json.loads(pay_json))
                    if calc != pay_hash:
                        _append_log("legal_tamper.log", {"action": "TAMPER_PAYLOAD", "name": self.name, "expected": pay_hash, "got": calc})
                        frappe.throw(_TAMPER_MSG, frappe.ValidationError)
        except Exception:
            pass

    def before_submit(self):
        must = ("company", "output_type", "reference_doctype", "reference_name", "schema_version", "generator_build", "source_hash", "payload_hash")
        missing = [f for f in must if not getattr(self, f, None)]
        if missing:
            _append_log("legal_policy.log", {"action": "MISSING_FIELDS", "name": self.name, "missing": missing})
            frappe.throw(f"خروجی قانونی ناقص است: {', '.join(missing)}", frappe.ValidationError)
