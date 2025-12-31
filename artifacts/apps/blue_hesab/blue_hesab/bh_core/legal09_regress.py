from __future__ import annotations

import datetime as _dt
import json
from typing import Any, Dict, List

import frappe

from blue_hesab.bh_core import smoke_invoices
from blue_hesab.bh_core.legal_hooks import _enabled_output_types


def _get_outputs(ref_doctype: str, ref_name: str) -> List[Dict[str, Any]]:
    return frappe.get_all(
        "BH Legal Output",
        filters={"reference_doctype": ref_doctype, "reference_name": ref_name},
        fields=[
            "name",
            "company",
            "output_type",
            "correction_reason",
            "previous_output",
            "payload_json",
            "payload_hash",
            "schema_version",
            "generator_build",
        ],
        order_by="creation asc",
    )


def run_legal09_regress(*, company: str = "BlueAPi") -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "ts": str(_dt.datetime.utcnow()),
        "company": company,
        "total": 4,
        "passed": 0,
        "failed": 0,
        "results": [],
    }

    sinv = None  # sales invoice name (prereq for cancel/amend)
    pinv = None  # purchase invoice name

    def ok(name: str, **kw):
        out["passed"] += 1
        out["results"].append({"name": name, "pass": True, **kw})

    def fail(name: str, error: str, **kw):
        out["failed"] += 1
        out["results"].append({"name": name, "pass": False, "error": error, **kw})

    enabled = _enabled_output_types(company)

    # 1) ISSUE: Sales Invoice submit must emit all enabled output types + payload schema v1 inside payload_json
    try:
        si = smoke_invoices.create_sales_invoice_and_submit(company=company, qty=1, rate=111111, vat_price_mode="Exclusive")
        sinv = si["sales_invoice"]
        rows = _get_outputs("Sales Invoice", sinv)

        have = sorted({r["output_type"] for r in rows if not r.get("correction_reason")})
        exp = sorted(enabled)

        if have != exp:
            raise Exception(f"issue outputs mismatch have={have} expected={exp}")

        # payload schema check (for issue rows)
        for r in rows:
            if r.get("correction_reason"):
                continue
            pj = r.get("payload_json") or "{}"
            obj = json.loads(pj)
            if "payload_schema_version" not in obj:
                raise Exception(f"missing payload_schema_version in {r['name']}")
        ok("LEGAL09-SI-ISSUE-EMIT+PAYLOAD", sales_invoice=sinv, enabled=enabled)
    except Exception as e:
        fail("LEGAL09-SI-ISSUE-EMIT+PAYLOAD", str(e))

    # 2) CANCEL: cancel must emit CANCEL outputs for all enabled types
    try:
        if not sinv:
            raise Exception("prereq failed: LEGAL09-SI-ISSUE-EMIT+PAYLOAD did not produce a Sales Invoice")
        smoke_invoices.cancel_doc(doctype="Sales Invoice", name=sinv)
        rows = _get_outputs("Sales Invoice", sinv)
        have = sorted({r["output_type"] for r in rows if r.get("correction_reason") == "CANCEL"})
        exp = sorted(enabled)
        if have != exp:
            raise Exception(f"cancel outputs mismatch have={have} expected={exp}")
        ok("LEGAL09-SI-CANCEL-EMIT", sales_invoice=sinv, enabled=enabled)
    except Exception as e:
        fail("LEGAL09-SI-CANCEL-EMIT", str(e))

    # 3) AMEND: create amendment and submit => must emit AMEND outputs for all enabled types
    try:
        if not sinv:
            raise Exception("prereq failed: LEGAL09-SI-ISSUE-EMIT+PAYLOAD did not produce a Sales Invoice")
        original = frappe.get_doc("Sales Invoice", sinv)
        amended = frappe.copy_doc(original)
        amended.amended_from = original.name
        amended.insert(ignore_permissions=True)
        amended.submit()

        rows = _get_outputs("Sales Invoice", amended.name)
        have = sorted({r["output_type"] for r in rows if r.get("correction_reason") == "AMEND"})
        exp = sorted(enabled)
        if have != exp:
            raise Exception(f"amend outputs mismatch have={have} expected={exp}")
        ok("LEGAL09-SI-AMEND-EMIT", original=sinv, amended=amended.name, enabled=enabled)
    except Exception as e:
        fail("LEGAL09-SI-AMEND-EMIT", str(e))

    # 4) Purchase Invoice smoke (issue+cancel) for parity
    try:
        pi = smoke_invoices.create_purchase_invoice_and_submit(company=company, qty=1, rate=123456, vat_price_mode="Exclusive")
        pinv = pi["purchase_invoice"]

        rows = _get_outputs("Purchase Invoice", pinv)
        have = sorted({r["output_type"] for r in rows if not r.get("correction_reason")})
        exp = sorted(enabled)
        if have != exp:
            raise Exception(f"PI issue outputs mismatch have={have} expected={exp}")

        smoke_invoices.cancel_doc(doctype="Purchase Invoice", name=pinv)
        rows = _get_outputs("Purchase Invoice", pinv)
        have = sorted({r["output_type"] for r in rows if r.get("correction_reason") == "CANCEL"})
        if have != exp:
            raise Exception(f"PI cancel outputs mismatch have={have} expected={exp}")

        ok("LEGAL09-PI-ISSUE+CANCEL", purchase_invoice=pinv, enabled=enabled)
    except Exception as e:
        fail("LEGAL09-PI-ISSUE+CANCEL", str(e))

    return out