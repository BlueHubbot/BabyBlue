from blue_hesab.bh_core.dim_testkit import apply_required_dims

class RegressResult(list):
    """
    Hybrid list+dict result:
      - behaves like a list of row dicts (iterable)
      - also exposes summary fields via .get() and ["passed"]/["failed"]/...
    """
    def __init__(self, rows, **summary):
        super().__init__(rows or [])
        self._summary = dict(summary or {})
        self._summary.setdefault("rows", rows or [])

    def get(self, key, default=None):
        return self._summary.get(key, default)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self._summary.get(key)
        return super().__getitem__(key)

    def to_dict(self):
        return dict(self._summary)

# /home/frappe/frappe-bench/apps/blue_hesab/blue_hesab/bh_core/vat_regress_si_v02.py
import frappe
from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error
from frappe.utils import today, flt


# -----------------------------
# Template name helpers
# -----------------------------

def _co_abbr(company: str) -> str:
    abbr = frappe.get_cached_value("Company", company, "abbr")
    return (abbr or "").strip()

def _sales_mixed_tpl(company: str, included: int) -> str:
    abbr = _co_abbr(company)
    mode = "INCL" if int(included) else "EXCL"
    return f"BH VAT MIXED Sales ({mode}) - {abbr}"

def _ensure_sales_templates_exist(company: str) -> None:
    tpl_excl = _sales_mixed_tpl(company, 0)
    tpl_incl = _sales_mixed_tpl(company, 1)
    missing = []
    if not frappe.db.exists("Sales Taxes and Charges Template", tpl_excl):
        missing.append(tpl_excl)
    if not frappe.db.exists("Sales Taxes and Charges Template", tpl_incl):
        missing.append(tpl_incl)
    if missing:
        raise Exception(
            "Missing required Sales Taxes and Charges Template(s):\n  - "
            + "\n  - ".join(missing)
            + "\nCreate/ensure MIXED templates first (Sales EXCL/INCL)."
        )


# -----------------------------
# Basic pickers
# -----------------------------

def _get_company():
    if frappe.db.exists("DocType", "BH Settings"):
        c = frappe.db.get_single_value("BH Settings", "default_company")
        if c and frappe.db.exists("Company", c):
            return c
    c = frappe.db.get_value("Company", {}, "name")
    if not c:
        raise Exception("No Company found.")
    return c

def _get_sales_vat_account():
    if not frappe.db.exists("DocType", "BH Settings"):
        return None
    return frappe.db.get_single_value("BH Settings", "default_sales_vat_account")

def _pick_income_account(company):
    acc = frappe.db.get_value("Account", {"company": company, "root_type": "Income", "is_group": 0}, "name")
    if acc:
        return acc
    acc = frappe.db.get_value("Account", {"company": company, "is_group": 0}, "name")
    if not acc:
        raise Exception("No leaf Account found.")
    return acc

def _ensure_customer():
    c = frappe.db.get_value("Customer", {"customer_name": "مشتری تست VAT"}, "name")
    if c:
        return c
    cg = frappe.db.get_value("Customer Group", {}, "name") or "All Customer Groups"
    tr = frappe.db.get_value("Territory", {}, "name") or "All Territories"
    doc = frappe.new_doc("Customer")
    doc.customer_name = "مشتری تست VAT"
    doc.customer_group = cg
    doc.territory = tr
    doc.save(ignore_permissions=True)
    return doc.name

def _require_items():
    items = [
        "BH-VAT-STD_9-TEST",
        "BH-VAT-ZERO-TEST",
        "BH-VAT-EXEMPT-TEST",
        "BH-VAT-EXPORT_0-TEST",
    ]
    missing = [i for i in items if not frappe.db.exists("Item", i)]
    if missing:
        raise Exception("Missing test Item(s): " + ", ".join(missing))
    return items


# -----------------------------
# Calculations & GL snapshots
# -----------------------------

def _vat_amount_from_si(si, vat_account):
    # Prefer explicit VAT row amount, fallback to total_taxes_and_charges
    if vat_account:
        for t in (si.get("taxes") or []):
            if t.get("account_head") == vat_account:
                return flt(t.get("tax_amount")), flt(t.get("rate"))
    return flt(si.get("total_taxes_and_charges")), None

def _gl_snapshot(company, voucher_no):
    rows = frappe.get_all(
        "GL Entry",
        filters={"company": company, "voucher_type": "Sales Invoice", "voucher_no": voucher_no},
        fields=["account", "debit", "credit", "party_type", "party", "creation"],
        order_by="creation asc",
        limit_page_length=2000,
    )
    agg = {}
    for r in rows:
        a = r["account"]
        agg.setdefault(a, {"debit": 0.0, "credit": 0.0})
        agg[a]["debit"] += flt(r["debit"])
        agg[a]["credit"] += flt(r["credit"])
    return rows, agg

def _find_party_line(gl_rows, customer):
    for r in gl_rows:
        if r.get("party_type") == "Customer" and r.get("party") == customer:
            return r["account"], flt(r["debit"]), flt(r["credit"])
    return None, 0.0, 0.0


# -----------------------------
# Builders
# -----------------------------

def _make_base_si(company, customer, income_account, rate=1_000_000):
    si = frappe.new_doc("Sales Invoice")
    si.company = company
    si.customer = customer
    si.posting_date = today()
    si.set_posting_time = 1

    for code in _require_items():
        si.append("items", {"item_code": code, "qty": 1, "rate": rate, "income_account": income_account})
    return si

def _set_qty(si, item_code, qty):
    for it in si.items:
        if it.item_code == item_code:
            it.qty = qty
    si.calculate_taxes_and_totals()

def _set_rate(si, item_code, rate):
    for it in si.items:
        if it.item_code == item_code:
            it.rate = rate
    si.calculate_taxes_and_totals()

def _add_actual_charge(si, income_account, amount):
    si.append(
        "taxes",
        {
            "charge_type": "Actual",
            "account_head": income_account,
            "description": "هزینه حمل/سرویس (تست)",
            "tax_amount": amount,
            "add_deduct_tax": "Add",
        },
    )
    si.calculate_taxes_and_totals()

def _remove_item(si, item_code):
    si.set("items", [it for it in si.items if it.item_code != item_code])
    si.calculate_taxes_and_totals()

def _make_return_doc(base_si_name):
    from erpnext.controllers.sales_and_purchase_return import make_return_doc
    ret = make_return_doc("Sales Invoice", base_si_name)
    ret.posting_date = today()
    ret.set_posting_time = 1
    return ret


# -----------------------------
# Assertions
# -----------------------------

def _expect_close(a, b, tol=0.01):
    return abs(flt(a) - flt(b)) <= tol

def _expected_template_for_scenario(company: str, sid: str):
    # Only SI-R05 is inclusive template. The rest are EXCL.
    if sid == "SI-R05":
        return _sales_mixed_tpl(company, 1)
    if sid.startswith("SI-") and sid != "SI-R08":
        return _sales_mixed_tpl(company, 0)
    return None


def _run_one(label, builder_fn, company, customer, vat_account):
    out = {"sid": label, "id": label, "name": None, "ok": True, "si": None, "err": None}

    try:
        si = builder_fn()

        # VAT-25 lock: no auto-apply in pipeline. The regress builders may leave taxes_and_charges empty.
        # We must set the expected Mixed template explicitly before save/submit.
        exp_tpl = _expected_template_for_scenario(company, label)
        if exp_tpl and not (si.get('taxes_and_charges') or '').strip():
            si.taxes_and_charges = exp_tpl
            # Ensure axis field matches the template (mode is authoritative under VAT-25).
            if hasattr(si, 'bh_vat_price_mode') and not (si.get('bh_vat_price_mode') or '').strip():
                si.bh_vat_price_mode = 'Inclusive' if '(INCL)' in exp_tpl else 'Exclusive'
                if si.bh_vat_price_mode == 'Inclusive':
                    si.set('bh_vat_inclusive_intent', 1)
            # Pull taxes rows from template (if controller supports it), then recalc.
            try:
                if hasattr(si, 'set_taxes_and_charges'):
                    si.set_taxes_and_charges()
            except Exception:
                pass
            try:
                si.calculate_taxes_and_totals()
            except Exception:
                pass


        # Save triggers VAT MIXED hooks (this is what we want to test)
        apply_required_dims(si, company=company)
        si.save(ignore_permissions=True)


        # Hard sanity: a Sales Invoice MUST NOT point to a Purchase template
        tac = (si.get("taxes_and_charges") or "").strip()
        if "BH VAT MIXED Purchase" in tac:
            raise Exception(
                "BUG: Sales Invoice got a PURCHASE template in taxes_and_charges:\n"
                f"  taxes_and_charges = {tac}\n"
                "Fix auto-apply logic in bh_before_validate_sales_invoice / vat_pipeline."
            )

        exp_tpl = _expected_template_for_scenario(company, label)
        if exp_tpl:
            if tac != exp_tpl:
                raise Exception(
                    "BUG: Wrong Sales template selected (template-axis mismatch):\n"
                    f"  expected = {exp_tpl}\n"
                    f"  got      = {tac or '(empty)'}\n"
                    "VAT-25 lock: regress must set taxes_and_charges explicitly (no auto-apply)."
                )

        si.submit()

        vat_amt, _ = _vat_amount_from_si(si, vat_account)
        gl_rows, gl_agg = _gl_snapshot(company, si.name)
        party_acc, party_dr, party_cr = _find_party_line(gl_rows, customer)

        out.update(
            {
                "si": si.name,
                "name": si.name,
                "doctype": "Sales Invoice",
                "docstatus": si.docstatus,
                "net": flt(si.net_total),
                "vat": flt(vat_amt),
                "grand": flt(si.grand_total),
                "party_account": party_acc,
                "party_debit": flt(party_dr),
                "party_credit": flt(party_cr),
                "vat_gl_debit": flt(gl_agg.get(vat_account, {}).get("debit", 0.0)) if vat_account else None,
                "vat_gl_credit": flt(gl_agg.get(vat_account, {}).get("credit", 0.0)) if vat_account else None,
                "taxes_and_charges": (si.get("taxes_and_charges") or None),
            }
        )
        return out

    except Exception:
        out["ok"] = False
        out["err"] = frappe.get_traceback()
        return out


# -----------------------------
# Public entrypoint
# -----------------------------

@frappe.whitelist()
def run_v02(rate=1000000):
    company = _get_company()
    customer = _ensure_customer()
    vat_account = _get_sales_vat_account()
    if not vat_account:
        raise Exception("BH Settings.default_sales_vat_account is not set.")
    income_account = _pick_income_account(company)

    # Ensure required Sales templates exist (template-axis)
    _ensure_sales_templates_exist(company)

    base_rate = flt(rate)
    results = []

    # R01 base
    def b1():
        return _make_base_si(company, customer, income_account, rate=base_rate)

    # R02 qty STD_9 = 2
    def b2():
        si = _make_base_si(company, customer, income_account, rate=base_rate)
        _set_qty(si, "BH-VAT-STD_9-TEST", 2)
        return si

    # R03 discount on STD_9 (rate * 0.9)
    def b3():
        si = _make_base_si(company, customer, income_account, rate=base_rate)
        _set_rate(si, "BH-VAT-STD_9-TEST", flt(base_rate) * 0.9)
        return si

    # R04 add actual charge 100k
    def b4():
        si = _make_base_si(company, customer, income_account, rate=base_rate)
        _add_actual_charge(si, income_account, 100000)
        return si

    # R05 inclusive intent should pick Sales (INCL) template (auto-apply)
    def b5():
        si = _make_base_si(company, customer, income_account, rate=base_rate)

        # Prefer the persisted UI field (what real users set)
        if hasattr(si, "bh_vat_price_mode"):
            si.bh_vat_price_mode = "Inclusive"

        # VAT-26: Inclusive must be explicit (intent), otherwise some pipelines
        # will downgrade to EXCL and SUBMIT will block due to template mismatch.
        if hasattr(si, "bh_vat_inclusive_intent"):
            si.bh_vat_inclusive_intent = 1

        # Keep flags too (for older hooks / safety)
        si.flags.bh_vat_price_mode = "Inclusive"
        si.flags.bh_vat_inclusive = 1
        si.flags.bh_vat_inclusive_intent = 1

        # Do NOT manually flip included_in_print_rate here; auto-apply must pick (INCL) template.
        return si

    # R06 rounding rate on STD_9 = 1,111,111
    def b6():
        si = _make_base_si(company, customer, income_account, rate=base_rate)
        _set_rate(si, "BH-VAT-STD_9-TEST", 1111111)
        return si

    # R07 no taxable item (remove STD_9)
    def b7():
        si = _make_base_si(company, customer, income_account, rate=base_rate)
        _remove_item(si, "BH-VAT-STD_9-TEST")
        return si

    # Run R01 first, then Return (R08)
    r01 = _run_one("SI-R01", b1, company, customer, vat_account)
    results.append(r01)

    if r01.get("ok") and r01.get("si"):
        def b8():
            return _make_return_doc(r01["si"])
        results.append(_run_one("SI-R08", b8, company, customer, vat_account))
    else:
        results.append({"sid": "SI-R08", "id": "SI-R08", "name": None, "ok": False, "si": None, "err": "Skipped because SI-R01 failed.", "pass": False})

    for sid, fn in [
        ("SI-R02", b2),
        ("SI-R03", b3),
        ("SI-R04", b4),
        ("SI-R05", b5),
        ("SI-R06", b6),
        ("SI-R07", b7),
    ]:
        results.append(_run_one(sid, fn, company, customer, vat_account))

    # VAT expectations (key checks)
    exp_vat = {
        "SI-R01": 90000.0,
        "SI-R02": 180000.0,
        "SI-R03": 81000.0,
        "SI-R04": 90000.0,
        # inclusive target (extracted VAT from 1,000,000 taxable item)
        "SI-R05": 82568.81,
        "SI-R06": 99999.99,
        "SI-R07": 0.0,
        "SI-R08": -90000.0,
    }

    for r in results:
        if not r.get("ok") or not r.get("si"):
            r["pass"] = False
            continue

        sid = r["id"]

        # VAT expected
        if sid in exp_vat:
            if not _expect_close(r.get("vat", 0.0), exp_vat[sid], tol=0.02):
                r["pass"] = False
                continue

        # GL direction checks for VAT account
        if sid != "SI-R08":
            if flt(r.get("vat", 0.0)) > 0 and flt(r.get("vat_gl_credit", 0.0)) <= 0:
                r["pass"] = False
                continue
        else:
            # Return should reverse -> VAT debit
            if abs(flt(r.get("vat", 0.0))) > 0 and flt(r.get("vat_gl_debit", 0.0)) <= 0:
                r["pass"] = False
                continue

        r["pass"] = True

    print("\n=== BH-EP01 v0.2 / SI MIXED REGRESSION (8 scenarios) ===")
    print("Company:", company)
    print("Customer:", customer)
    print("VAT Account:", vat_account)
    print("Income Account:", income_account)

    for r in results:
        key = r.get("id")
        if not r.get("ok"):
            print(f"\n[{key}] FAIL -> {r.get('si')}")
            print(r.get("err") or r.get("msg"))
            continue

        status = "PASS" if r.get("pass") else "FAIL"
        print(f"\n[{key}] {status} | {r.get('si')} | Net={r.get('net')} | VAT={r.get('vat')} | Grand={r.get('grand')}")
        print(
            f"  Customer({r.get('party_account')}): Dr={r.get('party_debit')} Cr={r.get('party_credit')} | "
            f"VAT GL: Dr={r.get('vat_gl_debit')} Cr={r.get('vat_gl_credit')} | "
            f"TAC={r.get('taxes_and_charges')}"
        )


    passed = sum(1 for r in results if r.get("ok") and r.get("pass"))
    failed = len(results) - passed
    ok = failed == 0
    return RegressResult(
        results,
        ver="BH-EP01 v0.2 / SI MIXED REGRESSION (8 scenarios)",
        company=company,
        customer=customer,
        vat_account=vat_account,
        income_account=income_account,
        total=len(results),
        passed=passed,
        failed=failed,
        ok=ok,
    )
