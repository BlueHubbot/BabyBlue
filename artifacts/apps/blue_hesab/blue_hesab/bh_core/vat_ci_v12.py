from __future__ import annotations

import json
from pathlib import Path

import frappe

from blue_hesab.bh_core import vat_ci
from blue_hesab.bh_core.vat_regress_intent_v01 import run_v01 as run_intent


def _summarize(rows_or_result):
    """
    Robust summarizer.

    Accepts:
      - list[dict]  (old style)
      - dict with {"rows": list[dict], ...}  (current intent regress output)
    """
    if rows_or_result is None:
        rows = []
    elif isinstance(rows_or_result, dict):
        rows = rows_or_result.get("rows") or []
    else:
        rows = rows_or_result or []

    # only count dict rows to avoid crashes
    safe_rows = [r for r in rows if isinstance(r, dict)]

    total = len(safe_rows)
    passed = sum(1 for r in safe_rows if r.get("ok") and r.get("pass"))
    failed = total - passed
    return {"total": total, "passed": passed, "failed": failed}



def run_ep01_v03_cli_v12(rate: int = 1000000, company: str = "BlueAPi", **kwargs):

    # --- VAT-13: Guard anti-regress (non-BH reject + price-mode flip) ---
    from blue_hesab.bh_core import vat_regress_vat13_guard
    _vat13_rate = 1000000
    try:
        _vat13_rate = float(locals().get("rate") or 1000000)
    except Exception:
        _vat13_rate = 1000000
    vat13 = vat_regress_vat13_guard.run_vat13_guard(rate=_vat13_rate)
    if not vat13.get("ok"):
        raise Exception("VAT-13 failed")

    # 1) run base CI (writes report file)
    base = vat_ci.run_ep01_v03_cli(rate=rate)

    # 2) run VAT-12 intent regress
    intent_rows = run_intent(company=company) or []
    intent_summary = _summarize(intent_rows)

    # 3) patch report JSON (best-effort)
    report_path = (base or {}).get("report")
    if report_path:
        p = Path(report_path)
        if not p.is_absolute():
            p = Path.cwd() / p
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                data = {}
            data["intent"] = {"summary": intent_summary, "rows": intent_rows}
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = bool((base or {}).get("ok")) and (intent_summary.get("failed") == 0)

    print("=== VAT-12 (CI V12) ===")
    print(f"Intent: {intent_summary}")
    if report_path:
        print(f"Report: {report_path}")

    if not ok:
        raise Exception("VAT-12 INTENT FAIL: some intent scenarios failed (or base CI failed). See report JSON.")

    base["intent"] = {"summary": intent_summary}
    base["ok"] = True
    return base
