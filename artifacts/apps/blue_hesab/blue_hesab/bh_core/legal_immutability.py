from __future__ import annotations

from typing import Dict, List

import frappe

_POLICY_LOCK_MSG = "ثبت/ویرایش خروجی‌های قانونی فقط از مسیر رسمی BlueHesab مجاز است."
_IMMUTABLE_MSG = "خروجی قانونی پس از ثبت نهایی غیرقابل تغییر است."
_DELETE_MSG = "حذف خروجی قانونی ثبت‌نهایی‌شده ممنوع است."


def _sql_escape(s: str) -> str:
    # minimal escape for embedding in CREATE TRIGGER literal
    return s.replace("\\", "\\\\").replace("'", "\\'")


def install_db_triggers() -> Dict[str, List[str]]:
    """Install MariaDB triggers for BH Legal Output:
    - Policy lock: block any INSERT/UPDATE/DELETE unless @bh_legal_emit=1 in the DB session.
    - Immutability: once docstatus=1, block any UPDATE and DELETE at DB level.
    """
    table = "tabBH Legal Output"

    # Drop any previous variants we might have created.
    drop_names = [
        # legacy
        "bh_legal_output_immutable_upd_v1",
        "bh_legal_output_immutable_del_v1",
        "bh_legal_output_policy_ins_v1",
        "bh_legal_output_policy_upd_v1",
        "bh_legal_output_policy_del_v1",
        # new (v2)
        "bh_legal_output_before_insert_v2",
        "bh_legal_output_before_update_v2",
        "bh_legal_output_before_delete_v2",
    ]
    for trig in drop_names:
        try:
            frappe.db.sql(f"DROP TRIGGER IF EXISTS {trig}")
        except Exception:
            pass

    policy_msg = _sql_escape(_POLICY_LOCK_MSG)
    imm_msg = _sql_escape(_IMMUTABLE_MSG)
    del_msg = _sql_escape(_DELETE_MSG)

    # BEFORE INSERT: only allowed when session var says so.
    frappe.db.sql(
        f"""
CREATE TRIGGER bh_legal_output_before_insert_v2
BEFORE INSERT ON `{table}`
FOR EACH ROW
BEGIN
    IF IFNULL(@bh_legal_emit, 0) <> 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MYSQL_ERRNO = 1644,
                MESSAGE_TEXT = '{policy_msg}';
    END IF;
END
"""
    )

    # BEFORE UPDATE: policy lock + immutable after submit
    frappe.db.sql(
        f"""
CREATE TRIGGER bh_legal_output_before_update_v2
BEFORE UPDATE ON `{table}`
FOR EACH ROW
BEGIN
    IF IFNULL(@bh_legal_emit, 0) <> 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MYSQL_ERRNO = 1644,
                MESSAGE_TEXT = '{policy_msg}';
    END IF;

    -- once submitted, fully immutable (also blocks cancel)
    IF IFNULL(OLD.docstatus, 0) = 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MYSQL_ERRNO = 1644,
                MESSAGE_TEXT = '{imm_msg}';
    END IF;
END
"""
    )

    # BEFORE DELETE: policy lock + forbid delete after submit
    frappe.db.sql(
        f"""
CREATE TRIGGER bh_legal_output_before_delete_v2
BEFORE DELETE ON `{table}`
FOR EACH ROW
BEGIN
    IF IFNULL(@bh_legal_emit, 0) <> 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MYSQL_ERRNO = 1644,
                MESSAGE_TEXT = '{policy_msg}';
    END IF;

    IF IFNULL(OLD.docstatus, 0) = 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MYSQL_ERRNO = 1644,
                MESSAGE_TEXT = '{del_msg}';
    END IF;
END
"""
    )

    try:
        frappe.db.commit()
    except Exception:
        pass

    return check_db_triggers()


def check_db_triggers() -> Dict[str, List[str]]:
    """Return installed trigger names for BH Legal Output (best-effort)."""
    try:
        rows = frappe.db.sql(
            """
            SELECT TRIGGER_NAME
            FROM information_schema.TRIGGERS
            WHERE TRIGGER_SCHEMA = DATABASE()
              AND EVENT_OBJECT_TABLE = 'tabBH Legal Output'
            ORDER BY TRIGGER_NAME
            """,
            as_dict=True,
        )
        return {"triggers": [r["TRIGGER_NAME"] for r in rows]}
    except Exception:
        return {"triggers": []}
