from __future__ import annotations

import frappe
from frappe.exceptions import ValidationError

from blue_hesab.bh_core.legal_audit import log_tamper


MSG_EDIT = "خروجی قانونی پس از «ثبت قطعی» غیرقابل تغییر است. برای اصلاح، خروجی جدید با «علت اصلاح» و ارجاع به خروجی قبلی صادر کنید."
MSG_CANCEL = "ابطال خروجی قانونی مجاز نیست. برای اصلاح/ابطال، خروجی اصلاحی جدید صادر کنید."
MSG_DELETE = "حذف خروجی قانونیِ ثبت‌شده مجاز نیست."


def _throw(msg: str) -> None:
    frappe.throw(msg, ValidationError)


def on_update_after_submit(doc, method=None):
    # Any edit after submit must be blocked (UI/API).
    try:
        log_tamper(
            "update_after_submit",
            name=getattr(doc, "name", "?"),
            details={"docstatus": int(getattr(doc, "docstatus", 0) or 0)},
        )
    except Exception:
        pass
    _throw(MSG_EDIT)


def on_cancel(doc, method=None):
    # Cancelling a legal output is never allowed.
    try:
        log_tamper(
            "cancel_attempt",
            name=getattr(doc, "name", "?"),
            details={"docstatus": int(getattr(doc, "docstatus", 0) or 0)},
        )
    except Exception:
        pass
    _throw(MSG_CANCEL)


def on_trash(doc, method=None):
    # Allow deleting drafts only (docstatus=0). Block submitted/cancelled.
    if int(getattr(doc, "docstatus", 0) or 0) == 0:
        return
    try:
        log_tamper(
            "trash_attempt",
            name=getattr(doc, "name", "?"),
            details={"docstatus": int(getattr(doc, "docstatus", 0) or 0)},
        )
    except Exception:
        pass
    _throw(MSG_DELETE)


TRG_UPD = "bh_legal_output_immutable_upd_v1"
TRG_DEL = "bh_legal_output_immutable_del_v1"


def install_db_triggers() -> dict:
    """
    Hard lock at DB level:
      - Block UPDATE when OLD.docstatus in (1,2)
      - Block DELETE when OLD.docstatus in (1,2)
    """
    table = "`tabBH Legal Output`"

    frappe.db.sql(f"DROP TRIGGER IF EXISTS `{TRG_UPD}`")
    frappe.db.sql(f"DROP TRIGGER IF EXISTS `{TRG_DEL}`")

    frappe.db.sql(
        f"""
        CREATE TRIGGER `{TRG_UPD}` BEFORE UPDATE ON {table}
        FOR EACH ROW
        BEGIN
            IF OLD.docstatus IN (1,2) THEN
                SIGNAL SQLSTATE "45000"
                    SET MESSAGE_TEXT = "BH Legal Output is immutable after submit";
            END IF;
        END
        """
    )

    frappe.db.sql(
        f"""
        CREATE TRIGGER `{TRG_DEL}` BEFORE DELETE ON {table}
        FOR EACH ROW
        BEGIN
            IF OLD.docstatus IN (1,2) THEN
                SIGNAL SQLSTATE "45000"
                    SET MESSAGE_TEXT = "BH Legal Output cannot be deleted after submit";
            END IF;
        END
        """
    )

    frappe.db.commit()
    return {"ok": True, "installed": [TRG_UPD, TRG_DEL]}


def uninstall_db_triggers() -> dict:
    frappe.db.sql(f"DROP TRIGGER IF EXISTS `{TRG_UPD}`")
    frappe.db.sql(f"DROP TRIGGER IF EXISTS `{TRG_DEL}`")
    frappe.db.commit()
    return {"ok": True, "dropped": [TRG_UPD, TRG_DEL]}


def check_db_triggers() -> dict:
    rows = frappe.db.sql(
        """
        SELECT TRIGGER_NAME
        FROM information_schema.TRIGGERS
        WHERE TRIGGER_SCHEMA = DATABASE()
          AND TRIGGER_NAME IN (%s, %s)
        """,
        (TRG_UPD, TRG_DEL),
        as_dict=True,
    )
    found = sorted([r["TRIGGER_NAME"] for r in rows])
    return {"found": found, "expected": [TRG_UPD, TRG_DEL], "ok": set(found) == {TRG_UPD, TRG_DEL}}


def smoke_legal04(name: str):
    out = {"name": name}

    # 1) raw db set_value (should be blocked by trigger)
    try:
        frappe.db.set_value("BH Legal Output", name, "modified_by", "Administrator")
        out["db_set_value_blocked"] = False
        out["db_set_value_error"] = None
    except Exception as e:
        out["db_set_value_blocked"] = True
        out["db_set_value_error"] = str(e)

    # 2) doc.db_set (should be blocked by trigger)
    try:
        doc = frappe.get_doc("BH Legal Output", name)
        doc.db_set("modified_by", "Administrator", update_modified=False)
        out["doc_db_set_blocked"] = False
        out["doc_db_set_error"] = None
    except Exception as e:
        out["doc_db_set_blocked"] = True
        out["doc_db_set_error"] = str(e)

    # 3) cancel (should be blocked by hook)
    try:
        doc = frappe.get_doc("BH Legal Output", name)
        doc.cancel()
        out["cancel_blocked"] = False
        out["cancel_error"] = None
    except Exception as e:
        out["cancel_blocked"] = True
        out["cancel_error"] = str(e)

    return out
