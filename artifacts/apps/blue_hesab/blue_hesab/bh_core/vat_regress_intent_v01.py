from __future__ import annotations

import json
import traceback
from typing import Any, Callable, Dict, List, Tuple

import frappe
from blue_hesab.bh_core import vat_pipeline as VP
from .vat_intent import vat11_resolve_price_mode

VERSION = "v0.7"

class _DummyDoc(dict):
    def get(self, key, default=None):
        return super().get(key, default)
    def set(self, key, value):
        self[key] = value

def _abbr(company: str) -> str:
    abbr = frappe.db.get_value("Company", company, "abbr")
    return (abbr or "").strip() or company

def _axis(mode: str) -> str:
    m = (mode or "").strip().lower()
    return "INCL" if m in ("incl", "inclusive", "in") else "EXCL"

def _doctype_for(kind: str) -> str:
    k = (kind or "").strip().lower()
    return "Sales Taxes and Charges Template" if k == "sales" else "Purchase Taxes and Charges Template"

def _expected_template(kind: str, mode: str, company: str) -> str:
    k = (kind or "").strip().lower()
    axis = _axis(mode)
    abbr = _abbr(company)
    return f"BH VAT MIXED {('Sales' if k=='sales' else 'Purchase')} ({axis}) - {abbr}"

def _infer(kind: str, mode: str, company: str):
    tpl, dt = VP._infer_mixed_template_name(
        kind=(kind or "").strip().lower(),
        mode=(mode or "").strip().lower(),
        company=company,
    )
    return tpl, dt

def _assert_callable(name: str) -> None:
    fn = getattr(VP, name, None)
    if not callable(fn):
        raise AssertionError(f"vat_pipeline.{name} is missing or not callable")

def _assert_infer(kind: str, mode: str, company: str) -> Dict[str, Any]:
    tpl, dt = _infer(kind, mode, company)

    expected_dt = _doctype_for(kind)
    expected_tpl = _expected_template(kind, mode, company)

    if dt != expected_dt:
        raise AssertionError(f"infer dt mismatch: got={dt!r} expected={expected_dt!r}")

    if tpl != expected_tpl:
        raise AssertionError(f"infer name mismatch: got={tpl!r} expected={expected_tpl!r}")

    if not frappe.db.exists(dt, tpl):
        raise AssertionError(f"template not found in DB: doctype={dt!r} name={tpl!r}")

    return {"tpl": tpl, "dt": dt}

def _assert_axis_ignores_template_and_sets_mode():
    d = _DummyDoc({
        "bh_vat_price_mode": "",
        "taxes_and_charges": "BH VAT MIXED Sales (INCL) - BA",
    })
    ax = VP._axis_from_doc(d)
    if ax != "EXCL":
        raise AssertionError(f"axis must be EXCL when mode empty; got={ax}")
    if d.get("bh_vat_price_mode") != "Exclusive":
        raise AssertionError(f"mode must be auto-set to Exclusive; got={d.get('bh_vat_price_mode')!r}")
    return {"axis": ax, "mode": d.get("bh_vat_price_mode")}

def _assert_axis_inclusive_when_mode_inclusive_even_if_template_excl():
    d = _DummyDoc({
        "bh_vat_price_mode": "Inclusive",
        "taxes_and_charges": "BH VAT MIXED Sales (EXCL) - BA",
    })
    ax = VP._axis_from_doc(d)
    if ax != "INCL":
        raise AssertionError(f"axis must be INCL when mode Inclusive; got={ax}")
    if d.get("bh_vat_price_mode") != "Inclusive":
        raise AssertionError("mode must stay canonical Inclusive")
    return {"axis": ax, "mode": d.get("bh_vat_price_mode")}

def _assert_legacy_set_official_template_is_noop():
    d = _DummyDoc({
        "company": "BlueAPi",
        "bh_vat_price_mode": "Exclusive",
        "taxes_and_charges": "BH VAT MIXED Sales (EXCL) - BA",
    })
    before = d.get("taxes_and_charges")
    VP._set_official_template_if_needed(d, kind="sales", company="BlueAPi", axis="EXCL", mode="Exclusive", is_submit=False)
    after = d.get("taxes_and_charges")
    if before != after:
        raise AssertionError(f"legacy helper must be NO-OP (no flips). before={before!r} after={after!r}")
    return True

def _run_case(sid: str, fn: Callable[[], Any]) -> Dict[str, Any]:
    row: Dict[str, Any] = {"sid": sid, "ok": True, "pass": True}
    try:
        out = fn()
        if out is not None:
            row["out"] = out
    except Exception as e:
        row["ok"] = False
        row["pass"] = False
        row["err"] = str(e) or repr(e) or "UNKNOWN_ERROR"
        row["traceback"] = traceback.format_exc()
    return row

def run_v01(company: str = "BlueAPi") -> Dict[str, Any]:
    cases: List[Tuple[str, Callable[[], Any]]] = [
        ("INT-SI-01", lambda: _assert_infer("sales", "exclusive", company)),
        ("INT-SI-02", lambda: _assert_infer("sales", "inclusive", company)),
        ("INT-SI-03", lambda: _assert_callable("validate_sales_invoice")),
        ("INT-SI-04", lambda: _assert_callable("bh_before_validate_sales_invoice")),
        ("INT-SI-05", _assert_axis_ignores_template_and_sets_mode),
        ("INT-SI-06", _assert_axis_inclusive_when_mode_inclusive_even_if_template_excl),
        ("INT-SI-07", _assert_legacy_set_official_template_is_noop),

        ("INT-PI-01", lambda: _assert_infer("purchase", "exclusive", company)),
        ("INT-PI-02", lambda: _assert_infer("purchase", "inclusive", company)),
        ("INT-PI-03", lambda: _assert_callable("validate_purchase_invoice")),
        ("INT-PI-04", lambda: _assert_callable("bh_before_validate_purchase_invoice")),
        ("INT-PI-05", _assert_axis_ignores_template_and_sets_mode),
    ]

    rows: List[Dict[str, Any]] = []
    failed = 0

    print(f"=== VAT-12 INTENT REGRESS {VERSION} ===")
    for sid, fn in cases:
        row = _run_case(sid, fn)
        rows.append(row)
        if row["pass"]:
            print(f"{sid}: PASS")
        else:
            failed += 1
            print(f"{sid}: FAIL - {row.get('err','UNKNOWN_ERROR')}")
    return {"ok": failed == 0, "failed": failed, "rows": rows}

def run_v01_cli(company: str = "BlueAPi") -> Dict[str, Any]:
    out = run_v01(company=company)
    
    # INT-SI-08
    doc = {"taxes_and_charges": "BH VAT MIXED Sales (INCL) - BA", "is_pos": 0, "bh_vat_price_mode": None}
    mode = vat11_resolve_price_mode("Sales Invoice", doc, company=company)
    assert mode == "Exclusive"

    # INT-SI-09
    doc = {"taxes_and_charges": "BH VAT MIXED Sales (EXCL) - BA", "is_pos": 1, "bh_vat_price_mode": None}
    mode = vat11_resolve_price_mode("Sales Invoice", doc, company=company)
    assert mode == "Inclusive"
    try:
        print(json.dumps(out, ensure_ascii=False))
    except Exception:
        pass
    return out
