#!/usr/bin/env python3
import os, csv, json, re, hashlib, sys, frappe
SITE=os.environ.get("SITE")
SRC="/srv/blue/overlay/i18n/fa/form_tour_fa_human.csv"
MAN="/srv/blue/overlay/manifests/overlay_rebrand_manifest.json"
if not SITE:
    print("SITE env required"); sys.exit(2)
frappe.init(site=SITE); frappe.connect()

def sha256p(p):
    if not os.path.exists(p): return None
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<16), b""): h.update(b)
    return h.hexdigest()

LAT=re.compile(r"[A-Za-z]")
seen=set(); rows=0; tr=0; un=0; latin=0
if os.path.exists(SRC):
    with open(SRC,encoding="utf-8") as f:
        for r in csv.DictReader(f):
            en=(r.get("source") or "").strip()
            if not en: continue
            rows+=1
            if en in seen: continue
            seen.add(en)
            n=frappe.db.get_value("Translation",{"language":"fa","source_text":en},"name")
            if n:
                tr+=1
                fa=(frappe.get_value("Translation",n,"translated_text") or "").strip()
                if LAT.search(fa): latin+=1
            else:
                un+=1
else:
    print("WARN: CSV not found:", SRC)

mf_ok=0; mf_total=0
if os.path.exists(MAN):
    d=json.load(open(MAN,encoding="utf-8"))
    for f in d.get("files",[]):
        p=f.get("path"); h=f.get("sha256")
        if not p or not h: continue
        mf_total+=1
        if sha256p(p)==h: mf_ok+=1
else:
    print("WARN: manifest not found:", MAN)

ok = (un==0 and latin==0 and tr==len(seen) and mf_total==mf_ok)
print("SELFTEST site={} rows={} distinct={} translated={} untranslated={} latin_left={} manifest_ok={}/{} RESULT={}".format(
    SITE, rows, len(seen), tr, un, latin, mf_ok, mf_total, "OK" if ok else "FAIL"
))
sys.exit(0 if ok else 1)
