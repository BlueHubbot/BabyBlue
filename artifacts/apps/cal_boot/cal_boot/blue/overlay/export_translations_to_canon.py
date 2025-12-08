import json
import pathlib

import frappe

# مسیر کانُن نهایی – همینی که می‌خواهی منبع اصلی باشد
OUT_PATH = pathlib.Path("/srv/blue/overlay/fixtures/translations_fa.canon.json")


def run():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = frappe.get_all(
        "Translation",
        filters={"language": "fa"},
        fields=["source_text", "translated_text"],
        limit=50000,
        order_by="source_text asc",
    )

    docs = []
    for r in rows:
        src = (r.get("source_text") or "").strip()
        dst = (r.get("translated_text") or "").strip()
        if not src or not dst:
            continue
        docs.append(
            {
                "doctype": "Translation",
                "language": "fa",
                "source_text": src,
                "translated_text": dst,
            }
        )

    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

    print(f"CANON_WRITTEN={OUT_PATH} COUNT={len(docs)}")
