# -*- coding: utf-8 -*-
"""blue_hesab.bh_core.regress.legal_ci

Entry point:
  bench --site <SITE> execute "blue_hesab.bh_core.regress.legal_ci.run_legal_suite" --kwargs '{"company":"BlueAPi"}'

Design goals:
- Single stable function for CI/runbook usage.
- No brittle imports of per-case helpers (those names change over time).
- Never crash the bench command: any exception becomes a FAIL result.
"""

from __future__ import annotations

import traceback
from typing import Any, Dict, List, Callable

import frappe  # noqa: F401  (kept to ensure frappe context is loaded)
from frappe.utils import now_datetime

from blue_hesab.bh_core.legal07_regress import run_legal07_regress
from blue_hesab.bh_core.legal08_regress import run_legal08_regress
from blue_hesab.bh_core.legal09_regress import run_legal09_regress


def _run_case(case_id: str, fn: Callable[..., Any], *, company: str) -> Dict[str, Any]:
    started = now_datetime()
    try:
        out = fn(company=company)

        ok = True
        if isinstance(out, bool):
            ok = out
        elif isinstance(out, dict):
            # Prefer explicit ok
            if "ok" in out:
                ok = bool(out.get("ok"))
            # Standard regression shape: {total, passed, failed, results}
            elif "failed" in out:
                ok = int(out.get("failed") or 0) == 0
            elif "passed" in out and "total" in out:
                ok = int(out.get("passed") or 0) == int(out.get("total") or 0)
            # Fallback: results list of dicts with {pass: bool}
            elif "results" in out and isinstance(out.get("results"), list):
                ok = all(bool(r.get("pass", True)) for r in out["results"] if isinstance(r, dict))
            else:
                ok = True

        return {
            "name": case_id,
            "ok": ok,
            "started_at": str(started),
            "ended_at": str(now_datetime()),
            "result": out,
        }
    except Exception:
        return {
            "name": case_id,
            "ok": False,
            "started_at": str(started),
            "ended_at": str(now_datetime()),
            "error": frappe.get_traceback(),
        }


def run_legal_suite(company: str = "BlueAPi", **kwargs) -> Dict[str, Any]:
    ts = str(now_datetime())

    cases = [
        ("LEGAL07", run_legal07_regress),
        ("LEGAL08", run_legal08_regress),
        ("LEGAL09", run_legal09_regress),
    ]

    results: List[Dict[str, Any]] = []
    for name, fn in cases:
        results.append(_run_case(name, fn, company=company))

    total = len(results)
    passed = sum(1 for r in results if r.get("ok"))
    failed = total - passed

    return {
        "ts": ts,
        "company": company,
        "total": total,
        "passed": passed,
        "failed": failed,
        "ok": failed == 0,
        "results": results,
    }
