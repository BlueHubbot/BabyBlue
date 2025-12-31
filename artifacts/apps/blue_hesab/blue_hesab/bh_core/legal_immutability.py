# -*- coding: utf-8 -*-
"""
DB-level policy lock + immutability for `BH Legal Output`.

We enforce:
- INSERT allowed only when session var @bh_legal_emit = 1 (blocks manual/UI inserts)
- UPDATE:
    - blocked unless @bh_legal_emit = 1
    - after submit (OLD.docstatus=1) immutable forever (even for emit path)
- DELETE:
    - blocked unless @bh_legal_emit = 1
    - after submit immutable (no delete)

This works alongside the UI-level lock in doctype controller (bh_legal_output.py).
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import List

import frappe


# Keep the exact Persian string for LEGAL-08 regress expectations
_POLICY_LOCK_MSG = "ثبت/ویرایش خروجی‌های قانونی فقط از مسیر رسمی BlueHesab مجاز است."
# Keep the exact English string historically used by DB triggers in regress logs
_IMMUTABLE_MSG = "BH Legal Output is immutable after submit"

_TABLE = "tabBH Legal Output"

TRG_BEFORE_INSERT = "bh_legal_output_before_insert_v2"
TRG_BEFORE_UPDATE = "bh_legal_output_before_update_v2"
TRG_BEFORE_DELETE = "bh_legal_output_before_delete_v2"


@contextmanager
def legal_emit_session():
    """
    Allow official pipeline to write BH Legal Output:
      - sets frappe.flags.bh_legal_emit (UI-level)
      - sets DB session var @bh_legal_emit = 1 (DB triggers)
    """
    old_flag = bool(getattr(frappe.flags, "bh_legal_emit", False))
    frappe.flags.bh_legal_emit = True
    try:
        frappe.db.sql("SET @bh_legal_emit = 1")
    except Exception:
        pass
    try:
        yield
    finally:
        try:
            frappe.db.sql("SET @bh_legal_emit = 0")
        except Exception:
            pass
        frappe.flags.bh_legal_emit = old_flag


def _drop_trigger(name: str) -> None:
    try:
        frappe.db.sql(f"DROP TRIGGER IF EXISTS `{name}`")
    except Exception:
        # ignore
        pass


def list_db_triggers() -> List[str]:
    rows = frappe.db.sql(
        "SHOW TRIGGERS WHERE `Table`=%s",
        (_TABLE,),
        as_dict=True,
    )
    return [r.get("Trigger") for r in rows if r.get("Trigger")]


def check_db_triggers(expected: List[str] | None = None) -> dict:
    """
    Helper for regress: returns found/expected and ok flag.
    """
    found = list_db_triggers()
    exp = expected or [TRG_BEFORE_INSERT, TRG_BEFORE_UPDATE, TRG_BEFORE_DELETE]
    return {"found": sorted(found), "expected": sorted(exp), "ok": set(exp).issubset(set(found))}


def install_db_triggers() -> dict:
    """
    Idempotent: drop old triggers and install v2 ones.
    """
    # drop any older versions too (best-effort)
    for name in [
        TRG_BEFORE_INSERT, TRG_BEFORE_UPDATE, TRG_BEFORE_DELETE,
        "bh_legal_output_immutable_upd_v1", "bh_legal_output_immutable_del_v1",
        "bh_legal_output_before_insert_v1", "bh_legal_output_before_update_v1", "bh_legal_output_before_delete_v1",
    ]:
        _drop_trigger(name)

    # INSERT: no OLD row here; only NEW
    frappe.db.sql(f"""
    CREATE TRIGGER `{TRG_BEFORE_INSERT}` BEFORE INSERT ON `{_TABLE}`
    FOR EACH ROW
    BEGIN
        IF IFNULL(@bh_legal_emit, 0) <> 1 THEN
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 1644, MESSAGE_TEXT = '{_POLICY_LOCK_MSG}';
        END IF;
    END
    """)

    # UPDATE: block unless emit session; then enforce immutability after submit
    frappe.db.sql(f"""
    CREATE TRIGGER `{TRG_BEFORE_UPDATE}` BEFORE UPDATE ON `{_TABLE}`
    FOR EACH ROW
    BEGIN
        IF IFNULL(@bh_legal_emit, 0) <> 1 THEN
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 1644, MESSAGE_TEXT = '{_POLICY_LOCK_MSG}';
        END IF;

        IF IFNULL(OLD.docstatus, 0) = 1 THEN
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 1644, MESSAGE_TEXT = '{_IMMUTABLE_MSG}';
        END IF;
    END
    """)

    # DELETE: block unless emit session; then enforce immutability after submit
    frappe.db.sql(f"""
    CREATE TRIGGER `{TRG_BEFORE_DELETE}` BEFORE DELETE ON `{_TABLE}`
    FOR EACH ROW
    BEGIN
        IF IFNULL(@bh_legal_emit, 0) <> 1 THEN
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 1644, MESSAGE_TEXT = '{_POLICY_LOCK_MSG}';
        END IF;

        IF IFNULL(OLD.docstatus, 0) = 1 THEN
            SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO = 1644, MESSAGE_TEXT = '{_IMMUTABLE_MSG}';
        END IF;
    END
    """)

    return {"triggers": list_db_triggers()}
