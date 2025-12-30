from __future__ import annotations

import json
import frappe
from frappe.model.document import Document
from frappe.exceptions import ValidationError

from blue_hesab.bh_core.legal_audit import log_tamper


MSG_MANUAL_CREATE = "ایجاد/ویرایش دستی خروجی قانونی مجاز نیست. این رکورد فقط توسط موتور BlueHesab تولید می‌شود."
MSG_HASH_MISMATCH = "عدم تطابق هش خروجی قانونی شناسایی شد. دستکاری داده‌ها مجاز نیست."


class BHLegalOutput(Document):
    """Immutable legal outputs (audit trail)."""

    def validate(self):
        # Block manual create/edit unless running inside internal emitter context.
        if not getattr(frappe.flags, "bh_legal_emit", False):
            if self.is_new() or int(getattr(self, "docstatus", 0) or 0) == 0:
                log_tamper("manual_write_blocked", name=getattr(self, "name", "(new)"))
                frappe.throw(MSG_MANUAL_CREATE, ValidationError)

    def before_submit(self):
        # Recompute hashes from stored JSON payloads and ensure consistency.
        self._bh_assert_hashes()

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
