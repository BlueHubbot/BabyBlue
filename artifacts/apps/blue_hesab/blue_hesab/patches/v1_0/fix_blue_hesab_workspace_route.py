import frappe

def execute():
    # فقط مطمئن می‌شویم لیبل/تیتر Workspace مالی = «بلو حساب» است
    new_title = "بلو حساب"
    label_candidates = ["حسابداری", "بلو حساب", "Accounting", "Accounts"]

    workspaces = frappe.get_all("Workspace", fields=["name", "label"])
    for ws in workspaces:
        if ws.label and ws.label in label_candidates:
            doc = frappe.get_doc("Workspace", ws.name)
            if hasattr(doc, "label"):
                doc.label = new_title
            if hasattr(doc, "title"):
                doc.title = new_title
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            break
