from __future__ import annotations

from collections import Counter, defaultdict
from typing import List

import frappe


def _s(v) -> str:
    return (v or "").strip()


def _missing_gl_dims(row) -> List[str]:
    miss = []
    if not _s(getattr(row, "bh_branch", None)):
        miss.append("bh_branch")
    if not _s(getattr(row, "bh_tafsili_1", None)):
        miss.append("bh_tafsili_1")
    try:
        rt = frappe.get_cached_value("Account", row.account, "report_type")
        if _s(rt) == "Profit and Loss" and not _s(getattr(row, "cost_center", None)):
            miss.append("cost_center")
    except Exception:
        pass
    return miss


def run_dim05_audit(company: str = "BlueAPi", limit: int = 5000) -> dict:
    rows = frappe.get_all(
        "GL Entry",
        filters={"company": company},
        fields=["name", "posting_date", "voucher_type", "voucher_no", "account", "bh_branch", "bh_tafsili_1", "cost_center"],
        order_by="posting_date desc, creation desc",
        limit_page_length=limit,
    )

    by_vt = defaultdict(Counter)
    total = 0
    bad = 0

    for r in rows:
        total += 1
        rr = frappe._dict(r)
        miss = _missing_gl_dims(rr)
        if not miss:
            continue
        bad += 1
        vt = _s(rr.get("voucher_type"))
        for f in miss:
            by_vt[vt][f] += 1

    top = []
    for vt, c in sorted(by_vt.items(), key=lambda kv: sum(kv[1].values()), reverse=True):
        top.append({"voucher_type": vt, "missing": dict(c)})

    out = {"company": company, "scanned": total, "bad": bad, "by_voucher_type": top[:30]}
    print("=== DIM-05 AUDIT ===")
    print(f"Company: {company} | scanned={total} | bad={bad}")
    for it in top[:20]:
        print(f"- {it['voucher_type']}: {it['missing']}")
    return out


def run_cli(company: str = "BlueAPi", limit: int = 5000) -> dict:
    return run_dim05_audit(company=company, limit=limit)
