import frappe
from blue_hesab.bh_core.errors import BH_VAT_E_GENERIC
from blue_hesab.bh_core.exc import raise_bh_vat_error
from blue_hesab.bh_core.vat_pipe_common import infer_mixed_template_name
from frappe.utils import today, flt

def _company():
    if frappe.db.exists('DocType','BH Settings'):
        c = frappe.db.get_single_value('BH Settings','default_company')
        if c and frappe.db.exists('Company', c):
            return c
    c = frappe.db.get_value('Company', {}, 'name')
    if not c:
        raise Exception('No Company found.')
    return c

def _sales_vat_account():
    if not frappe.db.exists('DocType','BH Settings'):
        return None
    return frappe.db.get_single_value('BH Settings','default_sales_vat_account')

def _pick_income(company):
    acc = frappe.db.get_value('Account', {'company': company, 'root_type': 'Income', 'is_group': 0}, 'name')
    if acc:
        return acc
    acc = frappe.db.get_value('Account', {'company': company, 'is_group': 0}, 'name')
    if not acc:
        raise Exception('No leaf account found.')
    return acc

def _pick_customer():
    c = frappe.db.get_value('Customer', {}, 'name')
    if c:
        return c
    # minimal create
    cg = frappe.db.get_value('Customer Group', {}, 'name') or 'All Customer Groups'
    tr = frappe.db.get_value('Territory', {}, 'name') or 'All Territories'
    doc = frappe.new_doc('Customer')
    doc.customer_name = 'مشتری تست VAT'
    doc.customer_group = cg
    doc.territory = tr
    doc.save(ignore_permissions=True)
    return doc.name

def _require_items():
    items = ['BH-VAT-STD_9-TEST','BH-VAT-ZERO-TEST','BH-VAT-EXEMPT-TEST','BH-VAT-EXPORT_0-TEST']
    miss = [i for i in items if not frappe.db.exists('Item', i)]
    if miss:
        raise Exception('Missing test items: ' + ', '.join(miss))
    return items

def _gl(company, voucher_no):
    rows = frappe.get_all(
        'GL Entry',
        filters={'company': company, 'voucher_type': 'Sales Invoice', 'voucher_no': voucher_no},
        fields=['account','debit','credit','party_type','party'],
        limit_page_length=2000
    )
    agg = {}
    for r in rows:
        a = r['account']
        agg.setdefault(a, {'dr':0.0,'cr':0.0})
        agg[a]['dr'] += flt(r['debit'])
        agg[a]['cr'] += flt(r['credit'])
    return agg

def _pick_required_link_value(parent_dt: str, fieldname: str, company: str | None = None) -> str:
    """Pick a value for a required Link field using field options (doctype) and best-effort filters."""
    meta = frappe.get_meta(parent_dt)
    df = meta.get_field(fieldname)
    if not df or df.fieldtype != "Link" or not df.options:
        raise ValidationError(f"BH DIM: field {parent_dt}.{fieldname} is not a Link or has no options")
    link_dt = df.options

    # prefer company-filtered records if possible
    try:
        link_meta = frappe.get_meta(link_dt)
        if company and link_meta and link_meta.has_field("company"):
            v = frappe.db.get_value(link_dt, {"company": company}, "name")
            if v:
                return v
    except Exception:
        pass

    v = frappe.db.get_value(link_dt, {}, "name")
    if not v:
        raise ValidationError(f"BH DIM: no records found for {link_dt} (needed for {parent_dt}.{fieldname})")
    return v


def _apply_required_invoice_dims(doc, company: str) -> None:
    """Set required header dimensions used by BH DIM policy."""
    if not doc.get("bh_branch"):
        doc.set("bh_branch", _pick_required_link_value(doc.doctype, "bh_branch", company=company))
    if not doc.get("bh_tafsili_1"):
        doc.set("bh_tafsili_1", _pick_required_link_value(doc.doctype, "bh_tafsili_1", company=company))


@frappe.whitelist()
def run_base(rate=1000000):
    company = _company()
    vat_acc = _sales_vat_account()
    if not vat_acc:
        raise Exception("BH Settings.default_sales_vat_account is not set.")

    income = _pick_income(company)
    customer = _pick_customer()
    items = _require_items()

    si = frappe.new_doc("Sales Invoice")
    si.company = company
    si.customer = customer
    si.posting_date = today()
    si.due_date = today()
    si.set_posting_time = 1

    # enforce price mode for template inference
    try:
        if hasattr(si, "bh_vat_price_mode"):
            si.bh_vat_price_mode = (getattr(si, "bh_vat_price_mode", None) or "Exclusive")
    except Exception:
        pass

    pm = (getattr(si, "bh_vat_price_mode", None) or "Exclusive")

    # VAT-11/25: explicitly set Mixed template for smoke (no empty taxes_and_charges)
    si.taxes_and_charges = infer_mixed_template_name(kind="sales", company=company, mode=pm, price_mode=pm)
    try:
        si.set_taxes_and_charges()
    except Exception:
        pass

    for code in items:
        si.append("items", {
            "item_code": code,
            "qty": 1,
            "rate": flt(rate),
            "income_account": income,
        })

    _apply_required_invoice_dims(si, company)

    si.insert(ignore_permissions=True)
    si.submit()

    # totals expectation: VAT only on STD_9 => 90k when rate=1,000,000
    exp_vat = flt(rate) * 0.09
    got_vat = flt(si.total_taxes_and_charges)

    gl = _gl(company, si.name)
    vat_line = gl.get(vat_acc, {"dr": 0.0, "cr": 0.0})

    print("\n=== SALES MIXED SMOKE (v0.2 / WI-01) ===")
    print("SI:", si.name)
    print("Net:", si.net_total, "VAT:", got_vat, "Grand:", si.grand_total)
    print("VAT Account:", vat_acc, "GL Dr:", vat_line["dr"], "GL Cr:", vat_line["cr"])

    ok = abs(got_vat - exp_vat) < 0.02 and vat_line["cr"] > 0
    if not ok:
        raise Exception("FAIL: VAT or GL does not match expectation.")

    print("PASS")
    return {
        "si": si.name,
        "net": si.net_total,
        "vat": got_vat,
        "grand": si.grand_total,
        "vat_gl_cr": vat_line["cr"],
    }

