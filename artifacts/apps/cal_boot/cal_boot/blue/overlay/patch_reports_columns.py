import json

import frappe


def has_persian(s: str) -> bool:
    if not s:
        return False
    return any("\u0600" <= ch <= "\u06FF" for ch in s)


def get_fa_translation(src: str) -> str | None:
    """Translation(language=fa, source_text=src) را برمی‌گرداند (اگر باشد و خالی نباشد)."""
    if not src:
        return None
    tr = frappe.db.get_value(
        "Translation",
        {"language": "fa", "source_text": src},
        "translated_text",
    )
    if not tr:
        return None
    tr = (tr or "").strip()
    if not tr:
        return None
    return tr


def patch_report_names() -> int:
    changed = 0
    rows = frappe.get_all(
        "Report",
        fields=["name", "report_name"],
        order_by="name",
    )
    for r in rows:
        src = (r.get("report_name") or "").strip()
        if not src or has_persian(src):
            continue

        dst = get_fa_translation(src)
        if not dst or dst == src:
            continue

        frappe.db.set_value(
            "Report",
            r["name"],
            "report_name",
            dst,
            update_modified=False,
        )
        changed += 1
    return changed


def patch_report_columns() -> int:
    """برچسب ستون‌ها را اگر ترجمه‌ی آماده داریم، فارسی می‌کند."""
    changed_reports = 0
    rows = frappe.get_all(
        "Report",
        fields=["name", "json"],
        order_by="name",
    )
    for r in rows:
        name = r["name"]
        js = (r.get("json") or "").strip()
        if not js:
            continue

        try:
            data = json.loads(js)
        except Exception:
            continue

        cols = data.get("columns") or []
        dirty = False

        for idx, col in enumerate(cols):
            # حالت dict (Material-style)
            if isinstance(col, dict):
                label = (col.get("label") or "").strip()
                if not label or has_persian(label):
                    continue

                dst = get_fa_translation(label)
                # اگر برای خود label ترجمه نداریم، یک بار با fieldname هم امتحان کن
                if not dst:
                    fn = (col.get("fieldname") or "").strip()
                    if fn and not has_persian(fn):
                        dst = get_fa_translation(fn)

                if not dst or dst == label:
                    continue

                col["label"] = dst
                dirty = True

            # حالت لیست/تاپل (بعضی Report Builderها)
            elif isinstance(col, (list, tuple)) and len(col) > 0:
                label = (col[0] or "").strip()
                if not label or has_persian(label):
                    continue

                dst = get_fa_translation(label)
                if not dst:
                    dst = get_fa_translation(label.replace("_", " "))

                if not dst or dst == label:
                    continue

                new_col = list(col)
                new_col[0] = dst
                cols[idx] = new_col
                dirty = True

        if dirty:
            data["columns"] = cols
            frappe.db.set_value(
                "Report",
                name,
                "json",
                json.dumps(data, ensure_ascii=False),
                update_modified=False,
            )
            changed_reports += 1

    return changed_reports


def run():
    name_changes = patch_report_names()
    col_changes = patch_report_columns()
    frappe.db.commit()
    print(
        f"PATCH_REPORT_NAMES={name_changes} "
        f"PATCH_REPORT_COLUMNS={col_changes}"
    )
