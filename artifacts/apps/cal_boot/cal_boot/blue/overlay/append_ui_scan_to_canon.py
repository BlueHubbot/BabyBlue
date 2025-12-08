import csv
import json
import pathlib

CANON_PATH = pathlib.Path("/srv/blue/overlay/fixtures/translations_fa.canon.json")
SCAN_PATH = pathlib.Path("/srv/blue/overlay/manifests/ui_untranslated_scan.csv")


def run():
    # کانُن فعلی را بخوان
    if CANON_PATH.exists():
        with CANON_PATH.open("r", encoding="utf-8") as f:
            try:
                docs = json.load(f)
            except Exception:
                docs = []
    else:
        docs = []

    # ست کلیدهای موجود (language, source_text)
    existing_keys = set()
    for d in docs:
        lang = (d.get("language") or "").strip()
        src = (d.get("source_text") or "").strip()
        if not lang or not src:
            continue
        existing_keys.add((lang, src))

    new_docs = []
    seen_src_in_scan = set()

    # CSV خروجی اسکن UI را بخوان
    with SCAN_PATH.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            src = (row.get("source_text") or "").strip()
            if not src:
                continue

            # فقط یک‌بار برای هر source_text
            if src in seen_src_in_scan:
                continue
            seen_src_in_scan.add(src)

            key = ("fa", src)
            if key in existing_keys:
                continue

            doc = {
                "doctype": "Translation",
                "language": "fa",
                "source_text": src,
                "translated_text": "",
            }
            new_docs.append(doc)
            existing_keys.add(key)

    if not new_docs:
        print("NO_NEW_KEYS_FROM_UI_SCAN")
        return

    docs.extend(new_docs)

    # مرتب‌سازی، برای کانُن تمیز
    docs_sorted = sorted(
        docs,
        key=lambda d: (
            d.get("language") or "",
            d.get("source_text") or "",
        ),
    )

    CANON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CANON_PATH.open("w", encoding="utf-8") as f:
        json.dump(docs_sorted, f, ensure_ascii=False, indent=2)

    print(f"APPENDED={len(new_docs)} TOTAL={len(docs_sorted)} PATH={CANON_PATH}")
