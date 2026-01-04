from __future__ import annotations

import json
import frappe
from frappe.utils import nowdate


def _hooks_has_dim_enforce() -> dict:
    try:
        ev = frappe.get_hooks("doc_events") or {}
        si = ev.get("Sales Invoice", {}) or {}
        pi = ev.get("Purchase Invoice", {}) or {}
        return {
            "sales_invoice_before_submit": si.get("before_submit"),
            "purchase_invoice_before_submit": pi.get("before_submit"),
        }
    except Exception as e:
        return {"error": f"get_hooks_failed: {e}"}



def _pick_source_si(company: str) -> str | None:
    rows = frappe.get_all(
        "Sales Invoice",
        filters={"company": company, "docstatus": 1},
        fields=["name"],
        order_by="modified desc",
        limit=1,
    )
    return rows[0]["name"] if rows else None


def _set_if_has_field(doc, fieldname: str, value):
    try:
        if getattr(doc, "meta", None) and doc.meta.has_field(fieldname):
            doc.set(fieldname, value)
    except Exception:
        pass


def _row_set_if_has_field(row, fieldname: str, value):
    try:
        if getattr(row, "meta", None) and row.meta.has_field(fieldname):
            row.set(fieldname, value)
    except Exception:
        pass


def _clone_si(src_name: str):
    src = frappe.get_doc("Sales Invoice", src_name)
    si = frappe.copy_doc(src)

    si.name = None
    si.docstatus = 0

    today = nowdate()

    # normalize key dates
    _set_if_has_field(si, "amended_from", None)
    _set_if_has_field(si, "posting_date", today)
    _set_if_has_field(si, "due_date", today)

    # Payment Terms/Schedule can regenerate past due dates → clear them for smoke
    _set_if_has_field(si, "payment_terms_template", None)
    try:
        if si.get("payment_schedule"):
            si.set("payment_schedule", [])
    except Exception:
        pass

    # Some setups validate "against_date" / "delivery_date" too
    _set_if_has_field(si, "delivery_date", today)
    _set_if_has_field(si, "transaction_date", today)

    return si


def _run_case(si, case_name: str, mutate_before_submit) -> dict:
    sp = f"DIM_SMOKE_{case_name}"
    out = {
        "case": case_name,
        "blocked": None,
        "stage": None,
        "error": None,
        "snapshot_after_save_reload": None,
        "direct_enforce_on_reloaded": None,
    }

    try:
        frappe.db.savepoint(sp)

        # 1) insert VALID doc first
        try:
            si.insert(ignore_permissions=True)
        except Exception as e:
            out["blocked"] = True
            out["stage"] = "insert"
            out["error"] = str(e)
            return out

        # 2) mutate right before submit (simulate user forgetting dims)
        try:
            mutate_before_submit(si)
        except Exception as e:
            out["blocked"] = True
            out["stage"] = "mutate"
            out["error"] = f"MUTATE_FAILED: {e}"
            return out

        # 3) SAVE as DRAFT (must be allowed; enforcement is submit-only)
        try:
            si.save(ignore_permissions=True)
        except Exception as e:
            out["blocked"] = True
            out["stage"] = "save"
            out["error"] = str(e)
            return out

        # 4) reload from DB (what submit flow effectively sees)
        try:
            si = frappe.get_doc("Sales Invoice", si.name)
        except Exception as e:
            out["blocked"] = True
            out["stage"] = "reload"
            out["error"] = str(e)
            return out

        # snapshot after reload
        try:
            items = si.get("items") or []
            snap_rows = []
            for idx, r in enumerate(items[:3], start=1):
                snap_rows.append({
                    "row": idx,
                    "cost_center": (r.get("cost_center") or ""),
                    "project": (r.get("project") or ""),
                })
            out["snapshot_after_save_reload"] = {
                "name": si.name,
                "bh_branch": si.get("bh_branch"),
                "bh_tafsili_1": si.get("bh_tafsili_1"),
                "bh_tafsili_2": si.get("bh_tafsili_2"),
                "rows": snap_rows,
            }
        except Exception:
            pass

        # 5) direct enforce probe on reloaded doc (diagnostic)
        try:
            from blue_hesab.bh_core.dimensions_policy import enforce_invoice_dimensions
            try:
                enforce_invoice_dimensions(si, method="before_submit")
                out["direct_enforce_on_reloaded"] = {"would_block": False}
            except Exception as e:
                out["direct_enforce_on_reloaded"] = {"would_block": True, "error": str(e)}
        except Exception as e:
            out["direct_enforce_on_reloaded"] = {"probe_failed": True, "error": str(e)}

        # 6) submit stage (REAL test)
        try:
            si.submit()
            out["blocked"] = False
            out["stage"] = "submit"
            out["error"] = "NOT_BLOCKED (unexpected) — enforcement still not executed on submit"
        except Exception as e:
            out["blocked"] = True
            out["stage"] = "submit"
            out["error"] = str(e)

        return out

    finally:
        try:
            frappe.db.rollback(save_point=sp)
        except Exception:
            try:
                frappe.db.rollback()
            except Exception:
                pass


def run_dim_smoke(company: str = "BlueAPi") -> str:
    """
    Terminal smoke test for P0.5 Dimensions Enforcement (submit-only).

    Strategy:
      - Clone latest submitted SI → insert as valid
      - Mutate dims right before submit → must block on submit
    """
    hooks = _hooks_has_dim_enforce()

    src = _pick_source_si(company)
    if not src:
        res = {"ok": False, "company": company, "error": "No submitted Sales Invoice found to clone.", "hooks": hooks}
        return json.dumps(res, ensure_ascii=False)

    results = {"ok": True, "company": company, "source_si": src, "hooks": hooks, "cases": []}

    # Case A: header missing on submit
    si_a = _clone_si(src)

    def mutate_header_missing(doc):
        # clear header dims right before submit
        doc.set("bh_branch", "")
        doc.set("bh_tafsili_1", "")
        # bh_tafsili_2 optional; keep or clear doesn't matter
        if doc.meta and doc.meta.has_field("bh_tafsili_2"):
            doc.set("bh_tafsili_2", "")

    results["cases"].append(_run_case(si_a, "HEADER_MISSING", mutate_header_missing))

    # Case B: row missing on submit
    si_b = _clone_si(src)

    def mutate_row_missing(doc):
        items = doc.get("items") or []
        if items:
            items[0].cost_center = ""
            items[0].project = ""

    results["cases"].append(_run_case(si_b, "ROW_MISSING", mutate_row_missing))

    return json.dumps(results, ensure_ascii=False)


def dim_enforce_state(company: str = "BlueAPi") -> str:
    from blue_hesab.bh_core.company_legal import get_company_legal_profile, should_enforce_dimensions, is_iran_mode_enabled

    p = get_company_legal_profile(company)
    res = {
        "company": company,
        "iran_mode": bool(is_iran_mode_enabled()),
        "profile": getattr(p, "name", None) if p else None,
        "enforce_dimensions_field": (int(getattr(p, "enforce_dimensions", 0) or 0) if p else None),
        "should_enforce_dimensions": bool(should_enforce_dimensions(company)),
    }
    return json.dumps(res, ensure_ascii=False)


def set_enforce_dimensions(company: str = "BlueAPi", value: int = 1) -> str:
    value = 1 if int(value or 0) == 1 else 0

    name = frappe.db.get_value("BH Company Legal Profile", {"company": company}, "name")
    if name:
        doc = frappe.get_doc("BH Company Legal Profile", name)
    else:
        doc = frappe.new_doc("BH Company Legal Profile")
        doc.company = company

    doc.enforce_dimensions = value
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return dim_enforce_state(company)
