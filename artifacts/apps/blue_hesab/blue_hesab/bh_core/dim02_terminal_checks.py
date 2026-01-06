# apps/blue_hesab/blue_hesab/bh_core/dim02_terminal_checks.py
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple

import frappe
from frappe.exceptions import ValidationError
from frappe.utils import nowdate


# ---------------------------------------------------------------------------
# Utilities (very small + defensive)
# ---------------------------------------------------------------------------

def _find_any_leaf_account(company: str, *, root_types: Optional[List[str]] = None) -> Optional[str]:
    cond = "AND is_group=0"
    params: Dict[str, Any] = {"company": company}
    if root_types:
        cond += " AND root_type IN %(root_types)s"
        params["root_types"] = tuple(root_types)
    rows = frappe.db.sql(
        f"""SELECT name FROM `tabAccount`
              WHERE company=%(company)s {cond}
              ORDER BY lft ASC
              LIMIT 1""",
        params,
        as_list=True,
    ) or []
    return rows[0][0] if rows else None


def _find_two_bankish_accounts(company: str) -> Tuple[Optional[str], Optional[str]]:
    rows = frappe.db.sql(
        """SELECT name FROM `tabAccount`
             WHERE company=%s AND is_group=0 AND root_type IN ('Bank','Cash')
             ORDER BY lft ASC
             LIMIT 5""",
        company,
        as_list=True,
    ) or []
    names = [r[0] for r in rows]
    if len(names) >= 2:
        return names[0], names[1]
    # fallback: any two leaf accounts
    rows2 = frappe.db.sql(
        """SELECT name FROM `tabAccount`
             WHERE company=%s AND is_group=0
             ORDER BY lft ASC
             LIMIT 2""",
        company,
        as_list=True,
    ) or []
    n2 = [r[0] for r in rows2]
    if len(n2) >= 2:
        return n2[0], n2[1]
    if len(n2) == 1:
        return n2[0], None
    return None, None


def _ensure_cost_center(company: str) -> Optional[str]:
    # pick a leaf CC if exists
    cc = frappe.db.sql(
        """SELECT name FROM `tabCost Center`
             WHERE company=%s AND is_group=0
             ORDER BY lft ASC
             LIMIT 1""",
        company,
        as_list=True,
    )
    if cc:
        return cc[0][0]

    # create a simple one under root (best-effort)
    root = frappe.db.sql(
        """SELECT name FROM `tabCost Center`
             WHERE company=%s
             ORDER BY lft ASC
             LIMIT 1""",
        company,
        as_list=True,
    )
    parent = root[0][0] if root else None
    try:
        doc = frappe.get_doc(
            {
                "doctype": "Cost Center",
                "cost_center_name": "BH Test CC",
                "company": company,
                "parent_cost_center": parent,
                "is_group": 0,
            }
        )
        doc.insert(ignore_permissions=True)
        return doc.name
    except Exception:
        return None

def _ensure_tafsili(company: str) -> str:
    """
    Return an existing BH Tafsili (per company if the DocType has that field).
    Tolerant to schema variations between versions and even partial migrations.
    """
    import frappe

    meta = frappe.get_meta("BH Tafsili")

    # Build the most compatible filters we can.
    filters = {}
    if meta.has_field("company") and company:
        filters["company"] = company

    # Prefer an "active" flag if present.
    if meta.has_field("is_active"):
        filters["is_active"] = 1
    elif meta.has_field("enabled"):
        filters["enabled"] = 1
    elif meta.has_field("disabled"):
        filters["disabled"] = 0
    elif meta.has_field("is_disabled"):
        filters["is_disabled"] = 0

    # Try with filters, then without, to survive mismatched columns.
    try:
        name = frappe.db.get_value("BH Tafsili", filters or {}, "name")
    except Exception:
        name = frappe.db.get_value("BH Tafsili", {}, "name")

    if name:
        return name

    # None exists -> create a minimal one (best-effort).
    data = {"doctype": "BH Tafsili"}

    if meta.has_field("title"):
        data["title"] = f"BH-DIM-AUTO ({company})"
    elif meta.has_field("tafsili_title"):
        data["tafsili_title"] = f"BH-DIM-AUTO ({company})"

    if meta.has_field("company") and company:
        data["company"] = company

    # Best-effort flags (only if fields exist in DocType)
    if meta.has_field("is_active"):
        data["is_active"] = 1
    elif meta.has_field("enabled"):
        data["enabled"] = 1
    elif meta.has_field("disabled"):
        data["disabled"] = 0
    elif meta.has_field("is_disabled"):
        data["is_disabled"] = 0

    doc = frappe.get_doc(data)

    try:
        doc.insert(ignore_permissions=True)
    except Exception:
        # If schema is partially migrated (meta says field exists but DB column missing),
        # retry without any "active" flags.
        for k in ("is_active", "enabled", "disabled", "is_disabled"):
            if hasattr(doc, k):
                try:
                    setattr(doc, k, None)
                except Exception:
                    pass
        doc.insert(ignore_permissions=True)

    return doc.name


def _ensure_branch(company: str) -> Optional[str]:
    b = frappe.db.sql("""SELECT name FROM `tabBranch` ORDER BY name ASC LIMIT 1""", as_list=True)
    if b:
        return b[0][0]
    try:
        doc = frappe.get_doc({"doctype": "Branch", "branch": "BH Test Branch", "company": company})
        doc.insert(ignore_permissions=True)
        return doc.name
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    name: str
    ok: bool
    details: Dict[str, Any]


def run_cli(company: str = "BlueAPi") -> Dict[str, Any]:
    """
    DIM-02 sanity checks:
    - JE: missing cost_center must block submit
    - JE: after setting cost_center, submit must pass
    - PE: missing cost_center must block submit (best-effort; skipped if prerequisites missing)
    """
    out: List[CheckResult] = []

    cc = _ensure_cost_center(company)

    # --- JE ------------------------------------------------------------------
    a1 = _find_any_leaf_account(company)  # any leaf
    a2 = _find_any_leaf_account(company, root_types=["Income", "Expense"]) or _find_any_leaf_account(company)
    if not (a1 and a2 and cc):
        out.append(CheckResult("DIM02-JE-PREREQ", False, {"company": company, "a1": a1, "a2": a2, "cc": cc}))
    else:
        # create draft JE with one missing CC
        je = frappe.get_doc(
            {
                "doctype": "Journal Entry",
                "company": company,
                "posting_date": nowdate(),
                "accounts": [
                    {"account": a1, "debit_in_account_currency": 1000, "cost_center": ""},
                    {"account": a2, "credit_in_account_currency": 1000, "cost_center": cc},
                ],
            }
        )
        je.insert(ignore_permissions=True)

        blocked = False
        err = None
        try:
            je.submit()
        except ValidationError as e:
            blocked = True
            err = str(e)

        out.append(CheckResult("DIM02-JE-01 submit blocked when CC missing", blocked, {"je": je.name, "error": err}))

        # fix and submit
        ok2 = False
        err2 = None
        try:
            je.reload()
            je.accounts[0].cost_center = cc
            je.save(ignore_permissions=True)
            je.submit()
            ok2 = True
        except Exception as e:
            err2 = str(e)
            ok2 = False

        out.append(CheckResult("DIM02-JE-02 submit passes after CC set", ok2, {"je": je.name, "error": err2}))

    # --- PE (best-effort internal transfer) ----------------------------------
    from_acc, to_acc = _find_two_bankish_accounts(company)
    if not (from_acc and to_acc and cc):
        out.append(
            CheckResult(
                "DIM02-PE-PREREQ",
                False,
                {"company": company, "from": from_acc, "to": to_acc, "cc": cc, "note": "skip PE if prerequisites missing"},
            )
        )
    else:
        # Payment Entry structure changes per ERPNext version; do best-effort.
        pe = frappe.get_doc(
            {
                "doctype": "Payment Entry",
                "company": company,
                "posting_date": nowdate(),
                "payment_type": "Internal Transfer",
                "paid_from": from_acc,
                "paid_to": to_acc,
                "paid_amount": 1000,
                "received_amount": 1000,
            }
        )
        # set missing CC explicitly if field exists
        try:
            if pe.meta.has_field("cost_center"):
                pe.cost_center = ""
        except Exception:
            pass

        pe.insert(ignore_permissions=True)

        blocked = False
        err = None
        try:
            pe.submit()
        except ValidationError as e:
            blocked = True
            err = str(e)
        except Exception as e:
            # if PE prerequisites differ, report as skip/error
            out.append(CheckResult("DIM02-PE-00 submit attempt", False, {"pe": pe.name, "error": str(e)}))
        else:
            out.append(CheckResult("DIM02-PE-00 submit attempt", True, {"pe": pe.name}))

        # only run "blocked" expectation if cost_center field exists
        try:
            has_cc = bool(pe.meta.has_field("cost_center"))
        except Exception:
            has_cc = True

        if has_cc:
            out.append(CheckResult("DIM02-PE-01 submit blocked when CC missing", blocked, {"pe": pe.name, "error": err}))

            ok2 = False
            err2 = None
            try:
                pe.reload()
                pe.cost_center = cc
                pe.save(ignore_permissions=True)
                pe.submit()
                ok2 = True
            except Exception as e:
                err2 = str(e)
                ok2 = False

            out.append(CheckResult("DIM02-PE-02 submit passes after CC set", ok2, {"pe": pe.name, "error": err2}))

    res = {
        "company": company,
        "total": len(out),
        "passed": sum(1 for x in out if x.ok),
        "failed": sum(1 for x in out if not x.ok),
        "results": [dict(name=x.name, ok=x.ok, details=x.details) for x in out],
    }
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return res


def check_custom_fields() -> Dict[str, Any]:
    """Quick meta check after DIM-02.B patch."""
    out: Dict[str, Any] = {}
    for dt in ("Journal Entry", "Payment Entry", "Journal Entry Account", "Payment Entry Deduction", "GL Entry"):
        try:
            m = frappe.get_meta(dt)
            out[dt] = {f: bool(m.has_field(f)) for f in ("bh_branch", "bh_tafsili_1", "bh_tafsili_2")}
        except Exception as e:
            out[dt] = {"error": str(e)}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return out


def run_dim04_gl_stamp_je(company: str = "BlueAPi") -> Dict[str, Any]:
    """DIM-04 smoke: JE header dims should not break submit and must stamp GL custom dims.

    Current DIM policy requires (for Journal Entry submit):
      - cost_center (standard)
      - bh_branch (BH)
      - bh_tafsili_1 (BH)
    """
    cc = _ensure_cost_center(company)
    br = _ensure_branch(company)
    t1 = _ensure_tafsili(company)

    if not cc:
        return {"ok": False, "error": "No Cost Center available", "company": company}
    if not br:
        return {"ok": False, "error": "No Branch available", "company": company}
    if not t1:
        return {"ok": False, "error": "No BH Tafsili available", "company": company}

    a1 = _find_any_leaf_account(company)
    a2 = _find_any_leaf_account(company, root_types=["Income", "Expense"])
    if not a1 or not a2:
        return {"ok": False, "error": "No suitable leaf accounts found", "a1": a1, "a2": a2}

    # Ensure JE has required BH header fields (if custom fields exist)
    je = frappe.get_doc(
        {
            "doctype": "Journal Entry",
            "company": company,
            "posting_date": nowdate(),
            "voucher_type": "Journal Entry",
            "user_remark": "BH DIM04 GL stamp (JE header)",
            "cost_center": cc,
            "bh_branch": br,
            "bh_tafsili_1": t1,
            "accounts": [
                {
                    "account": a1,
                    "debit_in_account_currency": 1000,
                    "credit_in_account_currency": 0,
                    "cost_center": cc,
                    "bh_branch": br,
                    "bh_tafsili_1": t1,
                },
                {
                    "account": a2,
                    "debit_in_account_currency": 0,
                    "credit_in_account_currency": 1000,
                    "cost_center": cc,
                    "bh_branch": br,
                    "bh_tafsili_1": t1,
                },
            ],
        }
    )
    je.insert(ignore_permissions=True)
    je.submit()

    rows = frappe.db.sql(
        """
        SELECT name, bh_branch, bh_tafsili_1
        FROM `tabGL Entry`
        WHERE voucher_type='Journal Entry' AND voucher_no=%s
        ORDER BY name
        """,
        (je.name,),
        as_dict=True,
    )

    ok = True
    errors = []

    if len(rows) < 2:
        ok = False
        errors.append(f"Expected >=2 GL Entry rows, got {len(rows)}")

    for r in rows:
        if (r.get("bh_branch") or "") != br:
            ok = False
            errors.append(f"GL {r.get('name')} bh_branch mismatch: {r.get('bh_branch')} != {br}")
        if (r.get("bh_tafsili_1") or "") != t1:
            ok = False
            errors.append(f"GL {r.get('name')} bh_tafsili_1 mismatch: {r.get('bh_tafsili_1')} != {t1}")

    return {
        "ok": ok,
        "company": company,
        "journal_entry": je.name,
        "bh_branch": br,
        "bh_tafsili_1": t1,
        "gl_rows": rows,
        "errors": errors,
    }


def _ensure_branch_named(company: str, name: str) -> str:
    b = frappe.db.get_value("Branch", {"name": name}, "name")
    if b:
        return b
    doc = frappe.get_doc({"doctype": "Branch", "branch": name, "company": company})
    doc.insert(ignore_permissions=True)
    return doc.name


def run_dim04_gl_stamp_je_linewise(company: str = "BlueAPi") -> dict:
    """
    DIM-04 line-aware smoke (JE):
    - JE with two account rows each having different bh_branch on the row
    - Also sets bh_tafsili_1 (required by DIM-02.B)
    Expect:
      - GL Entry.voucher_detail_no == JE Account row.name
      - GL Entry.bh_branch follows each row
      - GL Entry.bh_tafsili_1 follows each row (same t1 here)
    """
    import json
    from frappe.utils import nowdate

    def _ensure_tafsili() -> str | None:
        t = frappe.db.get_value("BH Tafsili", {}, "name")
        if t:
            return t
        try:
            d = frappe.get_doc({"doctype": "BH Tafsili", "title": "تفصیلی تست", "is_active": 1})
            d.insert(ignore_permissions=True)
            return d.name
        except Exception:
            return None

    cc = _ensure_cost_center(company)
    if not cc:
        res = {"ok": False, "note": "missing cost center"}
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return res

    # tafsili required by DIM-02.B
    t1 = _ensure_tafsili()
    if not t1:
        res = {"ok": False, "note": "missing BH Tafsili (cannot create/locate)"}
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return res

    # two DISTINCT branches
    br2 = _ensure_branch_named(company, "BH Test Branch 2")
    br1 = frappe.db.get_value("Branch", {"name": "اصلی"}, "name") or frappe.db.get_value("Branch", {}, "name") or _ensure_branch(company)
    if not br1:
        res = {"ok": False, "note": "missing branches"}
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return res
    if br1 == br2:
        br1 = _ensure_branch_named(company, "BH Test Branch 1")

    a1 = _find_any_leaf_account(company)
    a2 = _find_any_leaf_account(company, root_types=["Income", "Expense"]) or _find_any_leaf_account(company)
    if not (a1 and a2):
        res = {"ok": False, "note": "missing accounts", "a1": a1, "a2": a2}
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return res

    # Ensure row fields exist
    if not frappe.get_meta("Journal Entry Account").has_field("bh_branch"):
        res = {"ok": False, "note": "Journal Entry Account.bh_branch not installed"}
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return res
    if not frappe.get_meta("Journal Entry Account").has_field("bh_tafsili_1"):
        res = {"ok": False, "note": "Journal Entry Account.bh_tafsili_1 not installed"}
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return res

    # Create JE with different branch per row + required tafsili_1
    je = frappe.get_doc({
        "doctype": "Journal Entry",
        "company": company,
        "posting_date": nowdate(),
        "accounts": [
            {"account": a1, "debit_in_account_currency": 1000, "cost_center": cc, "bh_branch": br1, "bh_tafsili_1": t1},
            {"account": a2, "credit_in_account_currency": 1000, "cost_center": cc, "bh_branch": br2, "bh_tafsili_1": t1},
        ],
    })
    je.insert(ignore_permissions=True)
    je.submit()

    gl_rows = frappe.db.sql(
        """SELECT voucher_detail_no, bh_branch, bh_tafsili_1
             FROM `tabGL Entry`
            WHERE voucher_type=%s AND voucher_no=%s AND company=%s
            ORDER BY creation ASC""",
        (je.doctype, je.name, company),
        as_list=True,
    ) or []

    acc_rows = frappe.db.sql(
        """SELECT name, bh_branch, bh_tafsili_1
             FROM `tabJournal Entry Account`
            WHERE parenttype='Journal Entry' AND parent=%s
            ORDER BY idx ASC""",
        (je.name,),
        as_list=True,
    ) or []

    exp = {r[0]: {"bh_branch": (r[1] or "").strip(), "bh_tafsili_1": (r[2] or "").strip()} for r in acc_rows}
    got = {r[0]: {"bh_branch": (r[1] or "").strip(), "bh_tafsili_1": (r[2] or "").strip()} for r in gl_rows}

    ok = bool(gl_rows) and all(got.get(k) == v for k, v in exp.items() if k)

    res = {
        "ok": ok,
        "je": je.name,
        "branches": {"row1": br1, "row2": br2},
        "tafsili_1": t1,
        "expected": exp,
        "got": got,
        "gl_count": len(gl_rows),
        "je_accounts": acc_rows,
        "gl_rows": gl_rows,
    }
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return res


from frappe.exceptions import ValidationError

def run_dim02b_cli(company: str = "BlueAPi") -> dict:
    """
    DIM-02.B checks:
    - JE: missing bh_branch / bh_tafsili_1 blocks submit
    - JE: after setting them (header or row), submit passes
    - PE: missing header bh_branch / bh_tafsili_1 blocks submit
    """
    import json
    from frappe.utils import nowdate

    out = []

    cc = _ensure_cost_center(company)
    br = _ensure_branch(company)
    # BH Tafsili: pick any existing, else skip tafsili checks
    t1 = frappe.db.get_value("BH Tafsili", {}, "name")

    a1 = _find_any_leaf_account(company)
    a2 = _find_any_leaf_account(company, root_types=["Income", "Expense"]) or _find_any_leaf_account(company)

    if not (cc and br and a1 and a2):
        res = {"ok": False, "note": "missing prereqs", "cc": cc, "br": br, "a1": a1, "a2": a2, "t1": t1}
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return res

    if not t1:
        # create one best-effort
        try:
            d = frappe.get_doc({"doctype": "BH Tafsili", "title": "تفصیلی تست", "is_active": 1})
            d.insert(ignore_permissions=True)
            t1 = d.name
        except Exception:
            t1 = None

    # --- JE: missing dims should block
    je = frappe.get_doc({
        "doctype": "Journal Entry",
        "company": company,
        "posting_date": nowdate(),
        "accounts": [
            {"account": a1, "debit_in_account_currency": 1000, "cost_center": cc, "bh_branch": "", "bh_tafsili_1": ""},
            {"account": a2, "credit_in_account_currency": 1000, "cost_center": cc, "bh_branch": "", "bh_tafsili_1": ""},
        ],
    })
    je.insert(ignore_permissions=True)

    blocked = False
    err = None
    try:
        je.submit()
    except ValidationError as e:
        blocked = True
        err = str(e)
    out.append({"name": "DIM02B-JE-01 block when branch/tafsili missing", "ok": blocked, "je": je.name, "error": err})

    # set header (propagation should fill rows) and submit
    ok2 = False
    err2 = None
    try:
        je.reload()
        je.bh_branch = br
        if t1:
            je.bh_tafsili_1 = t1
        je.save(ignore_permissions=True)
        je.submit()
        ok2 = True
    except Exception as e:
        ok2 = False
        err2 = str(e)
    out.append({"name": "DIM02B-JE-02 pass after header dims set", "ok": ok2, "je": je.name, "error": err2})

    # --- PE: missing header dims should block
    from_acc, to_acc = _find_two_bankish_accounts(company)
    if from_acc and to_acc:
        pe = frappe.get_doc({
            "doctype": "Payment Entry",
            "company": company,
            "posting_date": nowdate(),
            "payment_type": "Internal Transfer",
            "paid_from": from_acc,
            "paid_to": to_acc,
            "paid_amount": 1000,
            "received_amount": 1000,
            "cost_center": cc,
            "bh_branch": "",
            "bh_tafsili_1": "",
        })
        pe.insert(ignore_permissions=True)

        blocked3 = False
        err3 = None
        try:
            pe.submit()
        except ValidationError as e:
            blocked3 = True
            err3 = str(e)
        out.append({"name": "DIM02B-PE-01 block when header branch/tafsili missing", "ok": blocked3, "pe": pe.name, "error": err3})

        ok4 = False
        err4 = None
        try:
            pe.reload()
            pe.bh_branch = br
            if t1:
                pe.bh_tafsili_1 = t1
            pe.save(ignore_permissions=True)
            pe.submit()
            ok4 = True
        except Exception as e:
            ok4 = False
            err4 = str(e)
        out.append({"name": "DIM02B-PE-02 pass after header dims set", "ok": ok4, "pe": pe.name, "error": err4})

    res = {"company": company, "total": len(out), "passed": sum(1 for x in out if x["ok"]), "failed": sum(1 for x in out if not x["ok"]), "results": out}
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return res

import json
import frappe

def run_dim04_audit_gl(
    company: str = "BlueAPi",
    from_date: str | None = None,
    limit: int = 200_000,
    sample_n: int = 30,
    top_n: int = 20,
    require_cc: str = "pl",  # "pl" | "all" | "none"
    **kwargs,
):
    """
    DIM04 - Audit GL rows for missing dimensions (branch/tafsili/cost_center).

    Accepts bench kwargs:
      - {"company":"BlueAPi"}
      - {"company":"BlueAPi","from":"2026-01-04"}  -> mapped to from_date
      - {"company":"BlueAPi","from_date":"2026-01-04"}
      - {"require_cc":"pl"} or "all" or "none"

    Output (JSON-safe):
      company, from, scanned, missing_dim_rows,
      missing_by_voucher_type, top_vouchers_with_missing_dims,
      je_voucher_detail_no_missing, sample[]
    """

    # accept reserved-ish key "from" coming from bench kwargs json
    if not from_date:
        from_date = (kwargs.get("from_date") or kwargs.get("from") or "2025-12-21")

    require_cc = (kwargs.get("require_cc") or require_cc or "pl").strip().lower()
    if require_cc not in ("pl", "all", "none"):
        require_cc = "pl"

    limit = int(kwargs.get("limit") or limit)
    sample_n = int(kwargs.get("sample_n") or sample_n)
    top_n = int(kwargs.get("top_n") or top_n)

    # --- fetch GL rows (bounded) ---
    rows = frappe.db.sql(
        """
        SELECT
            posting_date,
            voucher_type,
            voucher_no,
            voucher_detail_no,
            account,
            debit,
            credit,
            cost_center,
            bh_branch,
            bh_tafsili_1,
            bh_tafsili_2
        FROM `tabGL Entry`
        WHERE company = %(company)s
          AND IFNULL(is_cancelled, 0) = 0
          AND posting_date >= %(from_date)s
        ORDER BY posting_date DESC, creation DESC, name DESC
        LIMIT %(limit)s
        """,
        {"company": company, "from_date": from_date, "limit": limit},
        as_dict=True,
    )

    scanned = len(rows)
    if scanned == 0:
        return {
            "company": company,
            "from": from_date,
            "scanned": 0,
            "missing_dim_rows": 0,
            "missing_by_voucher_type": {},
            "top_vouchers_with_missing_dims": [],
            "je_voucher_detail_no_missing": 0,
            "sample": [],
        }

    # --- account classification cache (for require_cc="pl") ---
    acc_names = sorted({r.get("account") for r in rows if r.get("account")})
    acc_meta = {}
    if acc_names:
        # report_type exists on Account ("Balance Sheet" / "Profit and Loss") in ERPNext
        acc_rows = frappe.db.sql(
            """
            SELECT name, report_type, root_type, account_type
            FROM `tabAccount`
            WHERE name IN %(names)s
            """,
            {"names": tuple(acc_names)},
            as_dict=True,
        )
        for a in acc_rows:
            acc_meta[a["name"]] = a

    def is_pl_account(account: str | None) -> bool:
        if not account:
            return False
        a = acc_meta.get(account)
        if not a:
            return False
        rt = (a.get("report_type") or "").strip()
        if rt:
            return rt == "Profit and Loss"
        # fallback by root_type if report_type missing
        return (a.get("root_type") or "").strip() in ("Income", "Expense")

    # --- helpers ---
    def norm(v):
        # ensure JSON-safe
        if v is None:
            return None
        return str(v)

    def missing_fields_for_row(r) -> list[str]:
        miss = []
        if not (r.get("bh_branch") or "").strip():
            miss.append("bh_branch")
        if not (r.get("bh_tafsili_1") or "").strip():
            miss.append("bh_tafsili_1")

        if require_cc == "all":
            if not (r.get("cost_center") or "").strip():
                miss.append("cost_center")
        elif require_cc == "pl":
            if is_pl_account(r.get("account")) and not (r.get("cost_center") or "").strip():
                miss.append("cost_center")

        return miss

    # --- compute stats ---
    missing_dim_rows = 0
    missing_by_voucher_type: dict[str, int] = {}
    missing_by_voucher: dict[str, int] = {}  # "VT::VN" -> count

    je_vdn_no_missing = 0

    sample = []
    # sample rows: we keep latest sample_n rows, but we also add a "missing" flag
    for r in rows[: max(sample_n, 0)]:
        miss = missing_fields_for_row(r)
        sample.append(
            {
                "posting_date": norm(r.get("posting_date")),
                "vt": norm(r.get("voucher_type")),
                "vn": norm(r.get("voucher_no")),
                "vdn": norm(r.get("voucher_detail_no")),
                "account": norm(r.get("account")),
                "dr": float(r.get("debit") or 0.0),
                "cr": float(r.get("credit") or 0.0),
                "cc": norm(r.get("cost_center")),
                "branch": norm(r.get("bh_branch")),
                "t1": norm(r.get("bh_tafsili_1")),
                "t2": norm(r.get("bh_tafsili_2")),
                "missing": bool(miss),
                "missing_fields": miss,
            }
        )

    for r in rows:
        miss = missing_fields_for_row(r)
        vt = (r.get("voucher_type") or "").strip() or "?"
        vn = (r.get("voucher_no") or "").strip() or "?"
        key = f"{vt}::{vn}"

        if miss:
            missing_dim_rows += 1
            missing_by_voucher_type[vt] = missing_by_voucher_type.get(vt, 0) + 1
            missing_by_voucher[key] = missing_by_voucher.get(key, 0) + 1
        else:
            # metric used for JE linewise sanity: voucher_detail_no must be present and row is clean
            if vt == "Journal Entry" and (r.get("voucher_detail_no") is not None):
                je_vdn_no_missing += 1

    top_vouchers = sorted(missing_by_voucher.items(), key=lambda x: (-x[1], x[0]))[:top_n]
    top_vouchers_with_missing_dims = [[k, v] for k, v in top_vouchers]

    res = {
        "company": company,
        "from": from_date,
        "scanned": scanned,
        "missing_dim_rows": missing_dim_rows,
        "missing_by_voucher_type": missing_by_voucher_type,
        "top_vouchers_with_missing_dims": top_vouchers_with_missing_dims,
        "je_voucher_detail_no_missing": je_vdn_no_missing,
        "require_cc": require_cc,
        "sample": sample,
    }
    return res
