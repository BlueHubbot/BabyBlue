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

# /home/frappe/frappe-bench/apps/blue_hesab/blue_hesab/bh_core/vat_regress_pi_v01.py
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

def _purchase_mixed_tpl(company: str, included: int) -> str:
    abbr = _co_abbr(company)
    mode = "INCL" if int(included) else "EXCL"
    return f"BH VAT MIXED Purchase ({mode}) - {abbr}"

def _ensure_purchase_templates_exist(company: str) -> None:
    tpl_excl = _purchase_mixed_tpl(company, 0)
    tpl_incl = _purchase_mixed_tpl(company, 1)
    missing = []
    if not frappe.db.exists("Purchase Taxes and Charges Template", tpl_excl):
        missing.append(tpl_excl)
    if not frappe.db.exists("Purchase Taxes and Charges Template", tpl_incl):
        missing.append(tpl_incl)
    if missing:
        raise Exception(
            "Missing required Purchase Taxes and Charges Template(s):\n  - "
            + "\n  - ".join(missing)
            + "\nCreate/ensure MIXED templates first (Purchase EXCL/INCL)."
        )


# -----------------------------
# Pickers / bootstrap
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

def _get_purchase_vat_account():
    if not frappe.db.exists("DocType", "BH Settings"):
        return None
    return frappe.db.get_single_value("BH Settings", "default_purchase_vat_account")

def _pick_expense_account(company):
    # prefer an Expense leaf account
    acc = frappe.db.get_value(
        "Account",
        {"company": company, "root_type": "Expense", "is_group": 0},
        "name",
    )
    if acc:
        return acc
    # fallback: any leaf account
    acc = frappe.db.get_value("Account", {"company": company, "is_group": 0}, "name")
    if not acc:
        raise Exception("No leaf Account found.")
    return acc

def _ensure_supplier():
    name = "BH VAT REG Supplier"
    if frappe.db.exists("Supplier", name):
        return name
    s = frappe.new_doc("Supplier")
    s.supplier_name = name
    s.supplier_type = "Company"
    s.save(ignore_permissions=True)
    return s.name

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
# GL snapshots / VAT reads
# -----------------------------

def _gl_snapshot(company, voucher_no):
    rows = frappe.get_all(
        "GL Entry",
        filters={"company": company, "voucher_type": "Purchase Invoice", "voucher_no": voucher_no},
        fields=["account", "debit", "credit", "party_type", "party"],
        order_by="idx asc, creation asc",
        limit_page_length=2000,
    )
    # aggregate by account
    agg = {}
    for r in rows:
        a = r["account"]
        agg.setdefault(a, {"debit": 0.0, "credit": 0.0})
        agg[a]["debit"] += flt(r["debit"])
        agg[a]["credit"] += flt(r["credit"])
    return rows, agg

def _find_party_line(gl_rows, supplier):
    for r in gl_rows:
        if r.get("party_type") == "Supplier" and r.get("party") == supplier:
            return r["account"], flt(r["debit"]), flt(r["credit"])
    return None, 0.0, 0.0

def _vat_amount_from_pi(pi, vat_account):
    # best: read from taxes row account_head
    if vat_account:
        for t in (pi.get("taxes") or []):
            if t.get("account_head") == vat_account:
                return flt(t.get("tax_amount")), flt(t.get("rate"))
    # fallback: total taxes
    return flt(pi.get("total_taxes_and_charges")), None


# -----------------------------
# Builders
# -----------------------------

def _make_base_pi(company, supplier, expense_account, rate=1_000_000):
    pi = frappe.new_doc("Purchase Invoice")
    pi.company = company
    pi.supplier = supplier
    pi.posting_date = today()
    pi.set_posting_time = 1

    items = _require_items()

    # --- BH_PI_REQ_CATEGORY_V01 (tests only) ---
    if hasattr(pi, "category") and not (pi.get("category") or "").strip():
        try:
            df = frappe.get_meta("Purchase Invoice").get_field("category")
            if df and df.fieldtype == "Select" and (df.options or "").strip():
                opts = [o.strip() for o in (df.options or "").splitlines() if o.strip()]
                if opts:
                    pi.category = opts[0]
        except Exception:
            pass
        if not (pi.get("category") or "").strip():
            pi.category = "General"

    # last resort for any other custom mandatory fields
    pi.flags.ignore_mandatory = True

    for code in items:
        pi.append(
            "items",
            {"item_code": code, "qty": 1, "rate": rate, "expense_account": expense_account},
        )

    pi.save(ignore_permissions=True)  # triggers VAT hooks
    return pi

def _set_qty(pi, item_code, qty):
    for it in pi.items:
        if it.item_code == item_code:
            it.qty = qty
    pi.calculate_taxes_and_totals()

def _set_rate(pi, item_code, rate):
    for it in pi.items:
        if it.item_code == item_code:
            it.rate = rate
    pi.calculate_taxes_and_totals()

def _add_actual_charge(pi, expense_account, amount):
    pi.append(
        "taxes",
        {
            "charge_type": "Actual",
            "account_head": expense_account,
            "description": "هزینه حمل (تست)",
            "tax_amount": amount,
            "add_deduct_tax": "Add",
        },
    )
    pi.calculate_taxes_and_totals()

def _remove_item(pi, item_code):
    pi.set("items", [it for it in pi.items if it.item_code != item_code])
    pi.calculate_taxes_and_totals()

def _make_return(company, base_pi_name):
    from erpnext.controllers.sales_and_purchase_return import make_return_doc
    ret = make_return_doc("Purchase Invoice", base_pi_name)
    ret.posting_date = today()
    ret.set_posting_time = 1
    ret.save(ignore_permissions=True)
    ret.submit()
    return ret


# -----------------------------
# Assertions helpers
# -----------------------------

def _expect_close(a, b, tol=0.01):
    return abs(flt(a) - flt(b)) <= tol

def _expected_template_for_scenario(company: str, sid: str):
    # Only PI-R05 is inclusive template. The rest are EXCL.
    if sid == "PI-R05":
        return _purchase_mixed_tpl(company, 1)
    if sid.startswith("PI-") and sid != "PI-R08":
        return _purchase_mixed_tpl(company, 0)
    return None


def _run_one(label, builder_fn, company, supplier, expense_account, vat_account):
    out = {"sid": label, "id": label, "name": None, "ok": True, "pi": None, "err": None}

    try:
        pi = builder_fn()

        # VAT-25 lock: no auto-apply in pipeline. The regress builders may leave taxes_and_charges empty.
        # We must set the expected Mixed template explicitly before save/submit.
        exp_tpl = _expected_template_for_scenario(company, label)
        if exp_tpl and not (pi.get('taxes_and_charges') or '').strip():
            pi.taxes_and_charges = exp_tpl
            # Ensure axis field matches the template (mode is authoritative under VAT-25).
            if hasattr(pi, 'bh_vat_price_mode') and not (pi.get('bh_vat_price_mode') or '').strip():
                pi.bh_vat_price_mode = 'Inclusive' if '(INCL)' in exp_tpl else 'Exclusive'
                if pi.bh_vat_price_mode == 'Inclusive':
                    pi.set('bh_vat_inclusive_intent', 1)
            # Pull taxes rows from template (if controller supports it), then recalc.
            try:
                if hasattr(pi, 'set_taxes_and_charges'):
                    pi.set_taxes_and_charges()
            except Exception:
                pass
            try:
                pi.calculate_taxes_and_totals()
            except Exception:
                pass


        # Save triggers your VAT MIXED hooks (this is what we want to test)
        pi.save(ignore_permissions=True)

        # Hard sanity: a Purchase Invoice MUST NOT point to a Sales template
        tac = (pi.get("taxes_and_charges") or "").strip()
        if "BH VAT MIXED Sales" in tac:
            raise Exception(
                "BUG: Purchase Invoice got a SALES template in taxes_and_charges:\n"
                f"  taxes_and_charges = {tac}\n"
                "Fix auto-apply logic in bh_before_validate_purchase_invoice / vat_pipeline."
            )

        exp_tpl = _expected_template_for_scenario(company, label)
        if exp_tpl:
            if tac != exp_tpl:
                raise Exception(
                    "BUG: Wrong Purchase template selected (template-axis mismatch):\n"
                    f"  expected = {exp_tpl}\n"
                    f"  got      = {tac or '(empty)'}\n"
                    "VAT-25 lock: regress must set taxes_and_charges explicitly (no auto-apply)."
                )

        apply_required_dims(pi, company=company)
        pi.submit()


        vat_amt, _ = _vat_amount_from_pi(pi, vat_account)
        gl_rows, gl_agg = _gl_snapshot(company, pi.name)
        party_acc, party_dr, party_cr = _find_party_line(gl_rows, supplier)

        out.update(
            {
                "pi": pi.name,
                "name": pi.name,
                "doctype": "Purchase Invoice",
                "docstatus": pi.docstatus,
                "net": flt(pi.net_total),
                "vat": flt(vat_amt),
                "grand": flt(pi.grand_total),
                "party_account": party_acc,
                "party_credit": flt(party_cr),
                "vat_gl_debit": flt(gl_agg.get(vat_account, {}).get("debit", 0.0)) if vat_account else None,
                "vat_gl_credit": flt(gl_agg.get(vat_account, {}).get("credit", 0.0)) if vat_account else None,
                "taxes_and_charges": (pi.get("taxes_and_charges") or None),
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
def run_v01(rate=1000000):
    company = _get_company()
    supplier = _ensure_supplier()
    vat_account = _get_purchase_vat_account()
    expense_account = _pick_expense_account(company)

    if not vat_account:
        raise Exception("BH Settings.default_purchase_vat_account is not set.")

    # Ensure required Purchase templates exist (template-axis)
    _ensure_purchase_templates_exist(company)

    base_rate = flt(rate)
    results = []

    # R01 base
    def b1():
        return _make_base_pi(company, supplier, expense_account, rate=base_rate)

    # R02 qty STD_9 = 2
    def b2():
        pi = _make_base_pi(company, supplier, expense_account, rate=base_rate)
        _set_qty(pi, "BH-VAT-STD_9-TEST", 2)
        return pi

    # R03 item discount 10% on STD_9
    def b3():
        pi = _make_base_pi(company, supplier, expense_account, rate=base_rate)
        _set_rate(pi, "BH-VAT-STD_9-TEST", flt(base_rate) * 0.9)
        return pi

    # R04 add actual charge 100k
    def b4():
        pi = _make_base_pi(company, supplier, expense_account, rate=base_rate)
        _add_actual_charge(pi, expense_account, 100000)
        return pi

    # R05 inclusive intent should pick Purchase (INCL) template (auto-apply)
    def b5():
        pi = _make_base_pi(company, supplier, expense_account, rate=base_rate)

        # Prefer the persisted UI field (what real users set)
        if hasattr(pi, "bh_vat_price_mode"):
            pi.bh_vat_price_mode = "Inclusive"

        # VAT-26: Inclusive must be explicit (intent), otherwise some pipelines
        # will downgrade to EXCL and SUBMIT will block due to template mismatch.
        if hasattr(pi, "bh_vat_inclusive_intent"):
            pi.bh_vat_inclusive_intent = 1

        # Keep flags too (for older hooks / safety)
        pi.flags.bh_vat_price_mode = "Inclusive"
        pi.flags.bh_vat_inclusive = 1
        pi.flags.bh_vat_inclusive_intent = 1

        # Do NOT manually flip included_in_print_rate here; auto-apply must pick (INCL) template.
        return pi

    # R06 rounding rate on STD_9 = 1,111,111
    def b6():
        pi = _make_base_pi(company, supplier, expense_account, rate=base_rate)
        _set_rate(pi, "BH-VAT-STD_9-TEST", 1111111)
        return pi

    # R07 no taxable item (remove STD_9)
    def b7():
        pi = _make_base_pi(company, supplier, expense_account, rate=base_rate)
        _remove_item(pi, "BH-VAT-STD_9-TEST")
        return pi

    # R08 return against R01
    r01 = _run_one("PI-R01", b1, company, supplier, expense_account, vat_account)
    results.append(r01)

    if r01.get("ok") and r01.get("pi"):
        def b8():
            return _make_return(company, r01["pi"])
        results.append(_run_one("PI-R08", b8, company, supplier, expense_account, vat_account))
    else:
        results.append({"sid": "PI-R08", "id": "PI-R08", "name": None, "ok": False, "pi": None, "err": "Skipped because PI-R01 failed.", "pass": False})

    # run remaining
    for sid, fn in [
        ("PI-R02", b2),
        ("PI-R03", b3),
        ("PI-R04", b4),
        ("PI-R05", b5),
        ("PI-R06", b6),
        ("PI-R07", b7),
    ]:
        results.append(_run_one(sid, fn, company, supplier, expense_account, vat_account))

    # --- PASS/FAIL assertions (key ones) ---
    exp_vat = {
        "PI-R01": 90000.0,
        "PI-R02": 180000.0,
        "PI-R03": 81000.0,
        # inclusive target (extracted VAT from 1,000,000 taxable item)
        "PI-R05": 82568.81,
        "PI-R06": 99999.99,
        "PI-R07": 0.0,
        "PI-R08": -90000.0,
    }

    for r in results:
        if not r.get("ok") or not r.get("pi"):
            r["pass"] = False
            continue

        sid = r["id"]

        if sid in exp_vat:
            r["pass"] = _expect_close(r.get("vat", 0.0), exp_vat[sid], tol=0.02)
        else:
            r["pass"] = True

    # output compact
    print("\n=== BH-EP01 v0.1 / WI-03 / PI MIXED REGRESSION ===")
    print("Company:", company)
    print("Supplier:", supplier)
    print("VAT Account:", vat_account)
    print("Expense Account:", expense_account)

    for r in results:
        key = r.get("id")
        if not r.get("ok"):
            print(f"\n[{key}] FAIL -> {r.get('pi')}")
            print(r.get("err") or r.get("msg"))
            continue

        status = "PASS" if r.get("pass") else "FAIL"
        print(f"\n[{key}] {status} | {r.get('pi')} | Net={r.get('net')} | VAT={r.get('vat')} | Grand={r.get('grand')}")
        print(f"  Payable({r.get('party_account')}): Credit={r.get('party_credit')} | VAT GL: Dr={r.get('vat_gl_debit')} Cr={r.get('vat_gl_credit')}")

    passed = sum(1 for r in results if r.get("ok") and r.get("pass"))
    failed = len(results) - passed
    ok = failed == 0
    return RegressResult(
        results,
        ver="BH-EP01 v0.1 / WI-03 / PI MIXED REGRESSION",
        company=company,
        supplier=supplier,
        vat_account=vat_account,
        expense_account=expense_account,
        total=len(results),
        passed=passed,
        failed=failed,
        ok=ok,
    )
