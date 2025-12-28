import frappe

def execute():
    new_title = "بلو حساب"
    candidates = ["Accounts", new_title]

    for name in candidates:
        if frappe.db.exists("Workspace", name):
            ws = frappe.get_doc("Workspace", name)
            if hasattr(ws, "label"):
                ws.label = new_title
            if hasattr(ws, "title"):
                ws.title = new_title
            ws.save(ignore_permissions=True)
            frappe.db.commit()
            break
