#!/usr/bin/env python3
import sys, os, csv, json, hashlib, re
SITE = os.environ.get("SITE")
MAN  = os.environ.get("MANIFEST","/srv/blue/overlay/manifests/overlay_rebrand_manifest.json")
SRC  = "/srv/blue/overlay/i18n/fa/form_tour_fa_human.csv"
import frappe
frappe.init(site=SITE); frappe.connect()
def sha256p(p):
    if not os.path.exists(p): return None
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<16), b""): h.update(b)
    return h.hexdigest()
LAT=re.compile(r"[A-Za-z]")
rows=0; seen=set(); translated=0; untranslated=0; latin=0
if os.path.exists(SRC):
    with open(SRC,encoding="utf-8") as f:
        for r in csv.DictReader(f):
            en=(r.get("source") or "").strip()
            if not en: continue
            rows+=1
            if en in seen: continue
            seen.add(en)
            name=frappe.db.get_value("Translation",{"language":"fa","source_text":en},"name")
            if name:
                translated+=1
                fa=(frappe.get_value("Translation",name,"translated_text") or "").strip()
                if LAT.search(fa): latin+=1
            else:
                untranslated+=1
mf_total=0; mf_ok=0; items=[]
if os.path.exists(MAN):
    d=json.load(open(MAN,encoding="utf-8"))
    for f in d.get("files",[]):
        p=f.get("path"); h=f.get("sha256")
        if not p or not h: continue
        mf_total+=1
        ok=("OK" if sha256p(p)==h else "MISMATCH")
        items.append((p,ok))
        if ok=="OK": mf_ok+=1
print("SITE:", SITE)
print("SOURCES rows={} distinct={} translated={} untranslated={} latin_left={}".format(rows,len(seen),translated,untranslated,latin))
if mf_total:
    print("MANIFEST: {}/{} OK".format(mf_ok,mf_total))
    for p,st in items: print(" - {}: {}".format(st,p))
else:
    print("MANIFEST: not found or empty -> {}".format(MAN))
