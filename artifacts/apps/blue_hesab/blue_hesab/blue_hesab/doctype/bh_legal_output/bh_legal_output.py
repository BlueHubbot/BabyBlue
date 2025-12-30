from __future__ import annotations

import json
import frappe
from frappe.model.document import Document
from frappe.exceptions import ValidationError

from blue_hesab.bh_core.legal_audit import log_tamper, log_policy


MSG_MANUAL_CREATE = "ایجاد/ویرایش دستی خروجی قانونی مجاز نیست. این رکورد فقط توسط موتور BlueHesab تولید می‌شود."
MSG_HASH_MISMATCH = "عدم تطابق هش خروجی قانونی شناسایی شد. دستکاری داده‌ها مجاز نیست."
MSG_POLICY_LOCK = "مسیر غیرمجاز برای تولید/تغییر خروجی قانونی. فقط مسیرهای رسمی (صدور/ابطال/اصلاح) مجاز هستند."
MSG_CONTRACT = "خروجی قانونی ناقص است و قابل ثبت نیست (Contract)."


REQUIRED_FIELDS = [
    "company",
    "output_type",
    "reference_doctype",
    "reference_name",
    "schema_version",
    "generator_build",
    "source_hash",
    "payload_hash",
]


class BHLegalOutput(Document):
    """Immutable legal outputs (audit trail)."""

    def validate(self):
        # Hard policy lock: only internal emitter context may insert or modify (including drafts)
        if not getattr(frappe.flags, "bh_legal_emit", False):
            log_policy("blocked_non_emit_write", details={"name": getattr(self, "name", "(new)"), "docstatus": int(getattr(self, "docstatus", 0) or 0)})
            frappe.throw(MSG_POLICY_LOCK, ValidationError)

        # Keep previous behavior: block manual attempts early
        if not getattr(frappe.flags, "bh_legal_emit", False):
            if self.is_new() or int(getattr(self, "docstatus", 0) or 0) == 0:
                log_tamper("manual_write_blocked", name=getattr(self, "name", "(new)"))
                frappe.throw(MSG_MANUAL_CREATE, ValidationError)

    def before_submit(self):
        self._bh_assert_contract()
        self._bh_assert_hashes()

    def _bh_assert_contract(self):
        missing = [f for f in REQUIRED_FIELDS if not getattr(self, f, None)]
        if missing:
            log_tamper("contract_missing", name=self.name, details={"missing": missing})
            frappe.throw(MSG_CONTRACT + " Missing: " + ", ".join(missing), ValidationError)

    def _bh_assert_hashes(self):
        try:
            from blue_hesab.bh_core.legal_output import hash_obj
        except Exception:
            return

        def _rehash(field_json: str):
            if not field_json:
                return None
            try:
                obj = json.loads(field_json)
            except Exception:
                obj = field_json
            try:
                return hash_obj(obj)
            except Exception:
                return None

        src_h = _rehash(getattr(self, "source_json", None) or "")
        pay_h = _rehash(getattr(self, "payload_json", None) or "")

        if getattr(self, "source_hash", None) and src_h and src_h != self.source_hash:
            log_tamper("hash_mismatch_source", name=self.name, details={"expected": self.source_hash, "got": src_h})
            frappe.throw(MSG_HASH_MISMATCH, ValidationError)

        if getattr(self, "payload_hash", None) and pay_h and pay_h != self.payload_hash:
            log_tamper("hash_mismatch_payload", name=self.name, details={"expected": self.payload_hash, "got": pay_h})
            frappe.throw(MSG_HASH_MISMATCH, ValidationError)
