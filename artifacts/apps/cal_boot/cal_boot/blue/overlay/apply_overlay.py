import os, json, frappe, sys, pathlib

site = os.environ.get("SITE") or (sys.argv[1] if len(sys.argv)>1 else None)
assert site, "SITE is required"
frappe.init(site=site); frappe.connect()

base = "/srv/blue/overlay/fixtures"
tr_path = f"{base}/translation_form_tour_fa.json"
ps_path = f"{base}/property_setter_naming_series_fa.json"

def upsert_translation(doc):
    lang = doc.get("language") or "fa"
    src = (doc.get("source_text") or "").strip()
    fa  = (doc.get("translated_text") or "").strip()
    if not src or not fa: return False
    name = frappe.db.get_value("Translation", {"language":lang, "source_text":src}, "name")
    if name:
        d = frappe.get_doc("Translation", name)
        if (d.translated_text or "").strip() != fa:
            d.translated_text = fa
            d.save(ignore_permissions=True)
            return True
        return False
    frappe.get_doc({"doctype":"Translation","language":lang,"source_text":src,"translated_text":fa}).insert(ignore_permissions=True)
    return True

def upsert_prop_setter(d):
    key = {
        "doc_type": d.get("doc_type"),
        "field_name": d.get("field_name"),
        "property": d.get("property"),
        "doctype_or_field": d.get("doctype_or_field") or "DocField",
    }
    if not all(key.values()): return False
    name = frappe.db.get_value("Property Setter", key, "name")
    if name:
        ps = frappe.get_doc("Property Setter", name)
        changed = False
        val = d.get("value")
        ptype = d.get("property_type")
        if val is not None and ps.value != val:
            ps.value = val; changed = True
        if ptype and ps.property_type != ptype:
            ps.property_type = ptype; changed = True
        if changed:
            ps.save(ignore_permissions=True)
        return changed
    ins = {
        "doctype": "Property Setter",
        **key,
        "value": d.get("value"),
        "property_type": d.get("property_type") or "Data",
    }
    frappe.get_doc(ins).insert(ignore_permissions=True)
    return True

applied_tr = applied_ps = 0

if pathlib.Path(tr_path).exists():
    docs = json.load(open(tr_path, encoding="utf-8"))
    for doc in docs:
        if upsert_translation(doc): applied_tr += 1

if pathlib.Path(ps_path).exists():
    docs = json.load(open(ps_path, encoding="utf-8"))
    for d in docs:
        if upsert_prop_setter(d): applied_ps += 1

frappe.db.commit()
print(f"APPLIED_TRANSLATIONS={applied_tr} APPLIED_PROPERTY_SETTERS={applied_ps}")
