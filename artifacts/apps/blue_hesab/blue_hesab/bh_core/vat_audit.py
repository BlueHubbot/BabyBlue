# apps/blue_hesab/blue_hesab/bh_core/vat_audit.py
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import frappe
from frappe.exceptions import ValidationError


def _q_company(company: Optional[str]) -> Tuple[str, Tuple[Any, ...]]:
    if company:
        return " AND company=%s", (company,)
    return "", ()


def _missing_mode_clause() -> str:
    return "(bh_vat_price_mode IS NULL OR bh_vat_price_mode='' OR bh_vat_price_mode NOT IN ('Exclusive','Inclusive'))"


def _mismatch_clause(kind: str) -> Tuple[str, Tuple[Any, ...]]:
    # IMPORTANT: patterns must be passed as params (avoid % in query string)
    kind = (kind or "").strip().lower()
    like = "BH VAT MIXED Sales (%" if kind == "sales" else "BH VAT MIXED Purchase (%"
    clause = (
        "(taxes_and_charges LIKE %s AND ("
        "(bh_vat_price_mode='Inclusive' AND taxes_and_charges LIKE %s) OR "
        "(bh_vat_price_mode='Exclusive' AND taxes_and_charges LIKE %s)"
        "))"
    )
    params = (like, "%EXCL%", "%INCL%")
    return clause, params


def _table_for(doctype: str) -> str:
    if doctype == "Sales Invoice":
        return "`tabSales Invoice`"
    if doctype == "Purchase Invoice":
        return "`tabPurchase Invoice`"
    raise ValueError(f"Unsupported doctype: {doctype!r}")


def _assert_field_exists(doctype: str, fieldname: str) -> None:
    """
    Frappe v15: custom fields may not be in DocField. Use Meta first, then Custom Field.
    """
    try:
        meta = frappe.get_meta(doctype)
        if meta and meta.has_field(fieldname):
            return
    except Exception:
        pass

    if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": fieldname}):
        return

    if frappe.db.exists("DocField", {"parent": doctype, "fieldname": fieldname}):
        return

    raise ValidationError(f"Missing field {doctype}.{fieldname}. Did you run migrations?")


def audit_vat16(company: Optional[str] = None, sample: int = 10) -> Dict[str, Any]:
    """
    VAT-16 (audit): no mutations.
    - Missing/invalid bh_vat_price_mode
    - Mismatch between bh_vat_price_mode and taxes_and_charges (BH VAT MIXED only)
    """
    _assert_field_exists("Sales Invoice", "bh_vat_price_mode")
    _assert_field_exists("Purchase Invoice", "bh_vat_price_mode")

    sample = max(0, min(int(sample or 0), 50))

    out: Dict[str, Any] = {"company": company or None, "missing_mode": {}, "mismatch": {}}
    miss_clause = _missing_mode_clause()

    for dt, kind in (("Sales Invoice", "sales"), ("Purchase Invoice", "purchase")):
        table = _table_for(dt)
        q_c, p_c = _q_company(company)

        # ---- missing/invalid mode ----
        cnt = frappe.db.sql(
            f"SELECT COUNT(*) FROM {table} WHERE docstatus<2 AND {miss_clause}{q_c}",
            p_c,
        )[0][0]

        names: List[str] = []
        if sample and cnt:
            rows = frappe.db.sql(
                f"SELECT name FROM {table} WHERE docstatus<2 AND {miss_clause}{q_c} "
                "ORDER BY modified DESC LIMIT %s",
                p_c + (sample,),
            )
            names = [r[0] for r in rows]

        out["missing_mode"][dt] = {"count": int(cnt), "sample": names}

        # ---- mismatch mode vs template (BH VAT MIXED only) ----
        m_clause, m_params = _mismatch_clause(kind)

        m_cnt = frappe.db.sql(
            f"SELECT COUNT(*) FROM {table} WHERE docstatus<2 AND {m_clause}{q_c}",
            m_params + p_c,
        )[0][0]

        m_names: List[str] = []
        if sample and m_cnt:
            rows = frappe.db.sql(
                f"SELECT name FROM {table} WHERE docstatus<2 AND {m_clause}{q_c} "
                "ORDER BY modified DESC LIMIT %s",
                m_params + p_c + (sample,),
            )
            m_names = [r[0] for r in rows]

        out["mismatch"][dt] = {"count": int(m_cnt), "sample": m_names}

    return out


def audit_vat16_cli(company: Optional[str] = None, sample: int = 10) -> Dict[str, Any]:
    out = audit_vat16(company=company, sample=sample)
    print("=== VAT-16 AUDIT ===")
    print(json.dumps(out, ensure_ascii=False))
    return out


def backfill_missing_vat_mode(
    company: Optional[str] = None,
    limit: int = 500,
    dry_run: int = 1,
    include_submitted: int = 0,
) -> Dict[str, Any]:
    """
    VAT-16 (backfill):
    - ONLY sets missing/invalid bh_vat_price_mode -> 'Exclusive'
    - Default: ONLY Draft docs (docstatus=0)
    - Does NOT change taxes_and_charges (no silent flips)
    """
    _assert_field_exists("Sales Invoice", "bh_vat_price_mode")
    _assert_field_exists("Purchase Invoice", "bh_vat_price_mode")

    limit = max(1, min(int(limit or 0), 5000))
    dry_run = 1 if int(dry_run or 0) else 0
    include_submitted = 1 if int(include_submitted or 0) else 0

    docstatus_cond = "docstatus<2" if include_submitted else "docstatus=0"
    miss_clause = _missing_mode_clause()

    res: Dict[str, Any] = {
        "company": company or None,
        "limit": limit,
        "dry_run": bool(dry_run),
        "include_submitted": bool(include_submitted),
        "default_set": "Exclusive",
        "steps": [],
        "total_selected": 0,
        "total_updated": 0,
    }

    for dt in ("Sales Invoice", "Purchase Invoice"):
        table = _table_for(dt)
        q_c, p_c = _q_company(company)

        rows = frappe.db.sql(
            f"SELECT name FROM {table} WHERE {docstatus_cond} AND {miss_clause}{q_c} "
            "ORDER BY modified DESC LIMIT %s",
            p_c + (limit,),
        )
        names = [r[0] for r in rows]

        step = {"doctype": dt, "selected": len(names), "updated": 0, "sample": names[:10]}
        res["total_selected"] += len(names)

        if names and not dry_run:
            # LIMIT must be literal here (safe; bound by our cap)
            limit_n = int(len(names)) or 1
            frappe.db.sql(
                f"UPDATE {table} SET bh_vat_price_mode=%s "
                f"WHERE {docstatus_cond} AND {miss_clause}{q_c} "
                f"LIMIT {limit_n}",
                ("Exclusive",) + p_c,
            )
            step["updated"] = int(frappe.db.sql("SELECT ROW_COUNT()")[0][0] or 0)
            res["total_updated"] += step["updated"]

        res["steps"].append(step)

    if not dry_run:
        frappe.db.commit()

    return res


def backfill_missing_vat_mode_cli(
    company: Optional[str] = None,
    limit: int = 500,
    dry_run: int = 1,
    include_submitted: int = 0,
) -> Dict[str, Any]:
    out = backfill_missing_vat_mode(company=company, limit=limit, dry_run=dry_run, include_submitted=include_submitted)
    print("=== VAT-16 BACKFILL (missing/invalid bh_vat_price_mode -> Exclusive) ===")
    print(json.dumps(out, ensure_ascii=False))
    return out

def _expected_mode_from_mixed_template(taxes_and_charges: str) -> Optional[str]:
    s = (taxes_and_charges or "").upper()
    if "(INCL)" in s:
        return "Inclusive"
    if "(EXCL)" in s:
        return "Exclusive"
    # fallback if brackets missing
    if "INCL" in s:
        return "Inclusive"
    if "EXCL" in s:
        return "Exclusive"
    return None


def align_vat_mode_with_mixed_template(
    company: Optional[str] = None,
    limit: int = 5000,
    dry_run: int = 1,
    include_submitted: int = 1,
    only_mismatch: int = 1,
) -> Dict[str, Any]:
    """
    VAT-16 align:
    - For BH VAT MIXED docs only (Sales/Purchase)
    - Sets bh_vat_price_mode to match taxes_and_charges suffix (INCL/EXCL)
    - Does NOT change taxes_and_charges, items, or GL.
    """
    _assert_field_exists("Sales Invoice", "bh_vat_price_mode")
    _assert_field_exists("Purchase Invoice", "bh_vat_price_mode")

    limit = max(1, min(int(limit or 0), 5000))
    dry_run = 1 if int(dry_run or 0) else 0
    include_submitted = 1 if int(include_submitted or 0) else 0
    only_mismatch = 1 if int(only_mismatch or 0) else 0

    docstatus_cond = "docstatus<2" if include_submitted else "docstatus=0"
    q_c, p_c = _q_company(company)
    miss_clause = _missing_mode_clause()

    out: Dict[str, Any] = {
        "company": company or None,
        "limit": limit,
        "dry_run": bool(dry_run),
        "include_submitted": bool(include_submitted),
        "only_mismatch": bool(only_mismatch),
        "steps": [],
        "total_selected": 0,
        "total_would_update": 0,
        "total_updated": 0,
    }

    for dt, kind in (("Sales Invoice", "sales"), ("Purchase Invoice", "purchase")):
        table = _table_for(dt)
        like = "BH VAT MIXED Sales (%" if kind == "sales" else "BH VAT MIXED Purchase (%"

        if only_mismatch:
            where = (
                f"{docstatus_cond} AND taxes_and_charges LIKE %s AND ("
                f"{miss_clause} OR "
                f"(bh_vat_price_mode='Inclusive' AND taxes_and_charges LIKE %s) OR "
                f"(bh_vat_price_mode='Exclusive' AND taxes_and_charges LIKE %s)"
                f")"
            )
            params = (like, "%EXCL%", "%INCL%")
        else:
            where = f"{docstatus_cond} AND taxes_and_charges LIKE %s"
            params = (like,)

        rows = frappe.db.sql(
            f"SELECT name, taxes_and_charges, bh_vat_price_mode FROM {table} WHERE {where}{q_c} "
            "ORDER BY modified DESC LIMIT %s",
            params + p_c + (limit,),
            as_dict=True,
        )

        selected = len(rows)
        would_update = 0
        updated = 0
        sample_changes: List[Dict[str, Any]] = []

        for r in rows:
            name = r["name"]
            tpl = r.get("taxes_and_charges") or ""
            cur = (r.get("bh_vat_price_mode") or "").strip() or None
            exp = _expected_mode_from_mixed_template(tpl)

            if not exp:
                continue

            if cur != exp:
                would_update += 1
                if len(sample_changes) < 10:
                    sample_changes.append({"name": name, "from": cur, "to": exp, "tpl": tpl})

                if not dry_run:
                    frappe.db.set_value(dt, name, "bh_vat_price_mode", exp, update_modified=False)
                    updated += 1

        if not dry_run and updated:
            frappe.db.commit()

        out["total_selected"] += selected
        out["total_would_update"] += would_update
        out["total_updated"] += updated

        out["steps"].append(
            {
                "doctype": dt,
                "selected": selected,
                "would_update": would_update,
                "updated": updated,
                "sample_changes": sample_changes,
            }
        )

    return out


def align_vat_mode_with_mixed_template_cli(
    company: Optional[str] = None,
    limit: int = 5000,
    dry_run: int = 1,
    include_submitted: int = 1,
    only_mismatch: int = 1,
) -> Dict[str, Any]:
    out = align_vat_mode_with_mixed_template(
        company=company,
        limit=limit,
        dry_run=dry_run,
        include_submitted=include_submitted,
        only_mismatch=only_mismatch,
    )
    print("=== VAT-16 ALIGN (bh_vat_price_mode <- taxes_and_charges INCL/EXCL) ===")
    print(json.dumps(out, ensure_ascii=False))
    return out
