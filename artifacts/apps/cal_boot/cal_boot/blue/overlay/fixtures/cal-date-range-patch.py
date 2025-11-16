#!/usr/bin/env python3
import frappe, os

SITE="baba.bluehesab.ir"
SITES_PATH="/home/frappe/frappe-bench/sites"
PATCH_PATH="/home/frappe/bin/cal-date-range.js"

frappe.init(site=SITE, sites_path=SITES_PATH); frappe.connect()
with open(PATCH_PATH, "r", encoding="utf-8") as f:
    patch = f.read()

cnt=0
for row in frappe.get_all("Client Script", fields=["name"]):
    n = (row.get("name") or "")
    if n.startswith("CAL::GLOBAL::") or n.startswith("CAL::GLOBAL-LIST::"):
        doc = frappe.get_doc("Client Script", n)
        if "CAL :: DATE-RANGE-PATCH v1" not in doc.script:
            doc.script = patch + "\n\n" + doc.script
            doc.save(ignore_permissions=True)
            cnt += 1

frappe.db.commit()
print(f"OK: DATE-RANGE v1 injected into {cnt} scripts")
