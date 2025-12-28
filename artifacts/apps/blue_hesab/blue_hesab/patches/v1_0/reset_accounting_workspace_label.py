import frappe

def execute():
    # فقط Workspace اصلی Accounting را به حالت امن برمی‌گردانیم
    if not frappe.db.exists("Workspace", "Accounting"):
        return

    ws = frappe.get_doc("Workspace", "Accounting")
    if hasattr(ws, "label"):
        ws.label = "Accounting"
    if hasattr(ws, "title"):
        ws.title = "Accounting"
    ws.save(ignore_permissions=True)
    frappe.db.commit()
