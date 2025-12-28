// apps/blue_hesab/blue_hesab/public/js/vat_guard_ui.js
// BH VAT UI Guard — VAT-24.6
// - Button appears BOTH on form (custom panel) and inside the VAT modal.
// - Update-safe: NO duplicate rendering.
// - Avoids frappe.frm.set_intro stacking (uses stable DOM container).
// - Does NOT patch core frappe dialogs/msgprint.

(function () {
  "use strict";

  window.__BH_VAT_UI_VER__ = "VAT-24.7.0";
  if (window.__BH_VAT_UI_INSTALLED__) return;
  window.__BH_VAT_UI_INSTALLED__ = 1;

  // UI mode:
  // - "both"  : form panel button + modal button
  // - "panel" : only form panel button
  // - "modal" : only modal button
  window.__BH_VAT20_UI_MODE__ = window.__BH_VAT20_UI_MODE__ || "modal";

  window.__BH_VAT20_LAST_STATUS__ = null;
  window.__BH_VAT20_SUGGESTED__ = null;

  const STATE = {
    expected_cache: Object.create(null), // key -> {v, p}
    panel_dismissed_until: Object.create(null), // key -> ts
    last_panel_tick: 0,
    panel_timer: null,
    last_modal_tick: 0,
  };

  function norm(s) {
    return (s || "").toString().trim();
  }

  function kindFromFrm(frm) {
    if (!frm) return null;
    if (frm.doctype === "Sales Invoice") return "sales";
    if (frm.doctype === "Purchase Invoice") return "purchase";
    return null;
  }

  function modeToAxis(mode) {
    const m = norm(mode).toLowerCase();
    return m.includes("incl") ? "INCL" : "EXCL";
  }

  function tplAxis(tpl) {
    const s = norm(tpl).toUpperCase();
    if (s.includes("(INCL)")) return "INCL";
    if (s.includes("(EXCL)")) return "EXCL";
    return "";
  }

  function localSuggest(curTpl, expectedAxis) {
    const tpl = norm(curTpl);
    if (!tpl) return "";
    if (expectedAxis === "INCL" && tpl.toUpperCase().includes("(EXCL)")) return tpl.replace("(EXCL)", "(INCL)");
    if (expectedAxis === "EXCL" && tpl.toUpperCase().includes("(INCL)")) return tpl.replace("(INCL)", "(EXCL)");
    return "";
  }

  async function getExpectedFromServer(kind, axis, company) {
    const key = `${kind}|${axis}|${company || ""}`;
    const e = STATE.expected_cache[key] || (STATE.expected_cache[key] = { v: "", p: null });

    if (e.v) return e.v;
    if (e.p) return e.p;

    e.p = (async () => {
      try {
        const r = await frappe.call({
          method: "blue_hesab.bh_core.vat_pipeline.vat19_expected_mixed_template",
          args: { kind, axis, company: company || null },
          freeze: false,
        });
        const v = (r && r.message && r.message.expected) ? norm(r.message.expected) : "";
        e.v = v;
        return v;
      } catch (err) {
        return "";
      } finally {
        e.p = null;
      }
    })();

    return e.p;
  }

  function toast(indicator, msg) {
    try { frappe.show_alert({ message: msg, indicator: indicator || "blue" }); } catch (e) {}
  }

  // Loose context: works even when taxes_and_charges is empty or not mixed.
  function ctxFromFormLoose(frm) {
    const f = frm || window.cur_frm;
    if (!f || !f.doc) return { ok: false, why: "NO_FORM" };

    const kind = kindFromFrm(f);
    if (!kind) return { ok: false, why: "NOT_SI_PI" };

    const axis = modeToAxis(f.doc.bh_vat_price_mode);
    const curTpl = norm(f.doc.taxes_and_charges);
    const curAxis = tplAxis(curTpl);
    const company = f.doc.company || null;

    // mismatch only meaningful when template has an axis marker
    const mismatch = curAxis ? (axis !== curAxis) : false;

    return { ok: true, frm: f, kind, axis, curTpl, curAxis, mismatch, company };
  }

  async function expectedFor(ctx) {
    let expected = norm(window.__BH_VAT20_SUGGESTED__ || "");
    if (!expected) expected = norm(localSuggest(ctx.curTpl, ctx.axis));
    if (!expected) expected = norm(await getExpectedFromServer(ctx.kind, ctx.axis, ctx.company));
    if (expected) window.__BH_VAT20_SUGGESTED__ = expected;
    return expected;
  }

  async function applyExpected(frm) {
    const ctx = ctxFromFormLoose(frm);
    if (!ctx.ok) return;

    const expected = await expectedFor(ctx);
    if (!expected) return toast("orange", "BH VAT: قالب پیشنهادی پیدا نشد.");

    if (expected === norm(ctx.frm.doc.taxes_and_charges)) {
      return toast("green", "BH VAT: همین الان صحیح است.");
    }

    await ctx.frm.set_value("taxes_and_charges", expected);
    toast("green", `BH VAT: اعمال شد: ${expected} (ذخیره کنید)`);
    try { scheduleEnsurePanel(ctx.frm); } catch (e) {}
  }

  // ---------- Panel DOM (no stacking) ----------
  const PANEL_ID = "bh-vat20-panel";
  const PANEL_BTN_ID = "bh-vat20-panel-apply-btn";

  function panelKey(frm) {
    const dn = (frm && frm.doc && frm.doc.name) ? frm.doc.name : "";
    return `${frm ? frm.doctype : ""}|${dn}`;
  }

  function getPanelHost(frm) {
    try {
      if (frm && frm.dashboard && frm.dashboard.wrapper) {
        const w = frm.dashboard.wrapper;
        return w.get ? w.get(0) : w;
      }
    } catch (e) {}

    const w = frm && frm.page && frm.page.wrapper;
    const root = w ? (w.get ? w.get(0) : w) : null;
    if (!root) return null;

    return (
      root.querySelector(".form-dashboard") ||
      root.querySelector(".layout-main-section") ||
      root
    );
  }

  function removePanel(frm) {
    // Host can change across refreshes; remove globally to avoid duplicates.
    try {
      const els = document.querySelectorAll(`#${PANEL_ID}`);
      els.forEach((el) => { try { el.remove(); } catch (e) {} });
    } catch (e) {}
  }

  function renderPanel(frm, html, variant) {
    const host = getPanelHost(frm);
    if (!host) return;

    let el = document.getElementById(PANEL_ID);

    // If host changes between refreshes, move the existing element instead of creating a new one.
    if (el && el.getAttribute("data-bh-vat20") !== "panel") return;

    if (!el) {
      el = document.createElement("div");
      el.id = PANEL_ID;
      el.setAttribute("data-bh-vat20", "panel");
      el.style.margin = "0 0 10px 0";
    }

    if (!host.contains(el)) {
      try { host.prepend(el); }
      catch (e) { try { host.insertBefore(el, host.firstChild); } catch (x) {} }
    }

    // Kill any duplicates (can happen if host changed and old panel was rendered under a different container)
    try {
      const all = document.querySelectorAll(`#${PANEL_ID}`);
      all.forEach((n) => { if (n !== el) { try { n.remove(); } catch (e) {} } });
    } catch (e) {}

    const cls = (variant === "danger") ? "alert alert-danger" : "alert alert-warning";
    el.className = cls;
    el.style.display = "flex";
    el.style.alignItems = "center";
    el.style.gap = "10px";
    el.style.justifyContent = "space-between";

    el.innerHTML = `
      <div style="min-width:0">${html}</div>
      <div style="display:flex; gap:8px; align-items:center; flex:0 0 auto">
        <button id="${PANEL_BTN_ID}" type="button" class="btn btn-primary btn-sm">اعمال قالب پیشنهادی</button>
        <button type="button" class="btn-close" aria-label="Close"></button>
      </div>
    `;

    // close -> hide briefly
    const closeBtn = el.querySelector(".btn-close");
    if (closeBtn) {
      closeBtn.onclick = () => {
        STATE.panel_dismissed_until[panelKey(frm)] = Date.now() + 30_000;
        try { removePanel(frm); } catch (e) {}
      };
    }
  }

  // Delegated click: safe even if host changes
  function bindPanelClickOnce() {
    if (window.__BH_VAT20_PANEL_CLICK_BOUND) return;
    window.__BH_VAT20_PANEL_CLICK_BOUND = 1;

    document.addEventListener("click", async (ev) => {
      const t = ev && ev.target;
      if (!t || t.id !== PANEL_BTN_ID) return;
      try {
        ev.preventDefault();
        await applyExpected(window.cur_frm);
      } catch (e) {}
    }, true);
  }

  async function ensurePanel(frm) {
    const ctx = ctxFromFormLoose(frm);
    if (!ctx.ok) return;

    const mode = window.__BH_VAT20_UI_MODE__ || "both";
    const panelEnabled = (mode === "both" || mode === "panel");

    if (!panelEnabled) return removePanel(ctx.frm);

    // only drafts
    if ((ctx.frm.doc.docstatus || 0) !== 0) return removePanel(ctx.frm);

    // respect dismiss
    const dk = panelKey(ctx.frm);
    if (STATE.panel_dismissed_until[dk] && Date.now() < STATE.panel_dismissed_until[dk]) return;

    const expected = await expectedFor(ctx);
    const current = norm(ctx.frm.doc.taxes_and_charges);
    const needsFix = !!(expected && expected !== current);

    if (!needsFix) return removePanel(ctx.frm);

    bindPanelClickOnce();

    const curDisp = current || "—";
    const expDisp = expected || "—";
    const axisLabel = ctx.axis || "—";
    const curAxis = ctx.curAxis || "—";

    const html =
      `<b>BH VAT:</b> وضعیت قالب مالیات نیاز به اصلاح دارد.<br>` +
      `قیمت‌گذاری: <b>${axisLabel}</b> | قالب فعلی: <b>${curDisp}</b> (${curAxis})<br>` +
      `قالب پیشنهادی: <b>${expDisp}</b>`;

    renderPanel(ctx.frm, html, "danger");
  }

  // throttle panel updates (prevents flicker / async races)
  function scheduleEnsurePanel(frm) {
    const now = Date.now();
    STATE.last_panel_tick = now;

    if (STATE.panel_timer) clearTimeout(STATE.panel_timer);
    STATE.panel_timer = setTimeout(() => {
      try { ensurePanel(frm); } catch (e) {}
    }, 180);
  }

  // ---------- Modal detection ----------
  function modalLooksOpen(m) {
    try {
      if (!m) return false;
      const cls = m.classList || { contains: () => false };
      if (cls.contains("show") || cls.contains("in")) return true;
      const st = window.getComputedStyle(m);
      return st && st.display === "block" && st.visibility !== "hidden" && st.opacity !== "0";
    } catch (e) {
      return false;
    }
  }

  function zIndex(m) {
    try {
      const z = parseInt(window.getComputedStyle(m).zIndex || "0", 10);
      return Number.isFinite(z) ? z : 0;
    } catch (e) {
      return 0;
    }
  }

  function pickTopModal() {
    const all = Array.from(document.querySelectorAll(".modal")).filter(modalLooksOpen);
    if (!all.length) return null;
    all.sort((a, b) => zIndex(b) - zIndex(a));
    return all[0];
  }

  function looksLikeVatModal(modalEl) {
    const t = (modalEl && modalEl.innerText) ? modalEl.innerText : "";
    if (!t) return false;
    return /Taxes\s*&\s*Charges\s*Template|VAT|BH\s*VAT|قالب\s*پیشنهادی|انتخاب\s*فعلی\s*شما/i.test(t);
  }

  function extractTemplatesFromText(text) {
    const t = (text || "").toString();
    const re = /BH\s*VAT\s*MIXED\s*(Sales|Purchase)\s*\((INCL|EXCL)\)\s*-\s*BA/ig;
    const out = [];
    let m;
    while ((m = re.exec(t))) out.push(m[0].replace(/\s+/g, " ").trim());
    return out.filter((x, i) => out.indexOf(x) === i);
  }

  function modalCurrentFromText(text) {
    const m = (text || "").match(/انتخاب\s*فعلی\s*شما\s*:\s*([^\r\n]+)/i);
    if (m && m[1]) {
      const line = m[1].trim();
      const ts = extractTemplatesFromText(line);
      return ts.length ? ts[0] : line;
    }
    return "";
  }

  function modalSuggestedFromText(text) {
    const m = (text || "").match(/قالب\s*(?:صحیح\s*)?پیشنهادی\s*:\s*([^\r\n]+)/i);
    if (m && m[1]) {
      const line = m[1].trim();
      const ts = extractTemplatesFromText(line);
      return ts.length ? ts[0] : line;
    }
    const ts = extractTemplatesFromText(text || "");
    return ts.length ? ts[ts.length - 1] : "";
  }

  function ensureModalBar(modalEl) {
    const body = modalEl.querySelector(".modal-body") || modalEl;
    let bar = body.querySelector(".bh-vat20-bar");
    if (!bar) {
      bar = document.createElement("div");
      bar.className = "bh-vat20-bar";
      bar.style.cssText = "display:flex; gap:10px; align-items:center; padding:10px; border:1px solid var(--gray-200); border-radius:10px; margin-bottom:10px;";
      body.prepend(bar);
    }
    return bar;
  }

  async function injectOrUpdateModal(modalEl) {
    const mode = window.__BH_VAT20_UI_MODE__ || "both";
    if (!(mode === "both" || mode === "modal")) return "SKIP_MODAL_BY_MODE";

    if (!modalEl || !modalLooksOpen(modalEl)) return "NO_MODAL";
    if (!looksLikeVatModal(modalEl)) return "NOT_VAT_MODAL";

    const ctx = ctxFromFormLoose(window.cur_frm);
    if (!ctx.ok) return ctx.why;

    const text = modalEl.innerText || "";
    const modalCur = norm(modalCurrentFromText(text));
    const modalSug = norm(modalSuggestedFromText(text));

    // prefer explicit suggestion from modal text, else computed expected
    let suggested = modalSug || norm(window.__BH_VAT20_SUGGESTED__ || "");
    if (!suggested) suggested = norm(await expectedFor(ctx));
    if (suggested) window.__BH_VAT20_SUGGESTED__ = suggested;

    const modalMismatch = !!(modalCur && suggested && modalCur !== suggested);
    const currentTpl = norm(ctx.frm.doc.taxes_and_charges);
    const needsFix = !!(suggested && suggested !== currentTpl);

    if (!needsFix && !modalMismatch) return "NO_MISMATCH";

    const bar = ensureModalBar(modalEl);

    let hint = bar.querySelector(".bh-vat20-hint");
    if (!hint) {
      hint = document.createElement("span");
      hint.className = "bh-vat20-hint";
      hint.style.cssText = "opacity:.75; font-size:12px; margin-left:auto;";
      bar.appendChild(hint);
    }

    let btn = bar.querySelector("#bh-vat20-apply-btn");
    const existed = !!btn;
    if (!btn) {
      btn = document.createElement("button");
      btn.id = "bh-vat20-apply-btn";
      btn.type = "button";
      btn.className = "btn btn-primary";
      bar.prepend(btn);
    }

    btn.textContent = "اعمال قالب پیشنهادی";
    btn.onclick = async () => {
      try { await applyExpected(window.cur_frm); }
      catch (e) {
        try { frappe.msgprint({ title: "BH VAT", message: (e && e.message) ? e.message : String(e), indicator: "red" }); } catch (x) {}
      }
    };

    hint.textContent = suggested ? (`پیشنهاد: ${suggested}`) : "";

    // keep panel synced (important)
    try { if (window.cur_frm) scheduleEnsurePanel(window.cur_frm); } catch (e) {}

    window.__BH_VAT20_LAST_STATUS__ = {
      ver: window.__BH_VAT_UI_VER__,
      res: existed ? "UPDATED_OK" : "INJECTED_OK",
      ui_mode: mode,
      suggested: suggested || null,
      modal_current: modalCur || null,
      modal_mismatch: modalMismatch,
      frm_tpl: currentTpl || null,
      has_modal: true,
      modal_cls: modalEl.className,
      ts: new Date().toISOString(),
    };

    try { if (window.cur_frm) scheduleEnsurePanel(window.cur_frm); } catch (e) {}

    return existed ? "UPDATED_OK" : "INJECTED_OK";
  }

  function tryInjectModal() {
    const now = Date.now();
    if (now - STATE.last_modal_tick < 150) return;
    STATE.last_modal_tick = now;

    const m = pickTopModal();
    const res = m ? injectOrUpdateModal(m) : "NO_MODAL";

    if (!window.__BH_VAT20_LAST_STATUS__ || window.__BH_VAT20_LAST_STATUS__.res === "NO_MODAL") {
      window.__BH_VAT20_LAST_STATUS__ = {
        ver: window.__BH_VAT_UI_VER__,
        res,
        suggested: window.__BH_VAT20_SUGGESTED__,
        has_modal: !!m,
        modal_cls: m ? m.className : null,
        ts: new Date().toISOString(),
      };
    }
  }

  window.__BH_VAT20_TRY_INJECT = tryInjectModal;
  window.__BH_VAT20_FORCE_INJECT = function () {
    try { if (window.cur_frm) scheduleEnsurePanel(window.cur_frm); } catch (e) {}
    tryInjectModal();
    return window.__BH_VAT20_LAST_STATUS__;
  };

  function install() {
    // Bootstrap modal event is enough; no prototype patching.
    if (window.jQuery) {
      window.jQuery(document).on("shown.bs.modal", ".modal", function () {
        setTimeout(() => { try { if (window.cur_frm) scheduleEnsurePanel(window.cur_frm); } catch (e) {} tryInjectModal(); }, 0);
      });
    }

    // Panel sync with doc edits
    frappe.ui.form.on("Sales Invoice", {
      refresh(frm) { scheduleEnsurePanel(frm); tryInjectModal(); },
      taxes_and_charges(frm) { scheduleEnsurePanel(frm); tryInjectModal(); },
      bh_vat_price_mode(frm) { scheduleEnsurePanel(frm); tryInjectModal(); },
    });
    frappe.ui.form.on("Purchase Invoice", {
      refresh(frm) { scheduleEnsurePanel(frm); tryInjectModal(); },
      taxes_and_charges(frm) { scheduleEnsurePanel(frm); tryInjectModal(); },
      bh_vat_price_mode(frm) { scheduleEnsurePanel(frm); tryInjectModal(); },
    });

    setTimeout(() => {
      try { if (window.cur_frm) scheduleEnsurePanel(window.cur_frm); } catch (e) {}
      tryInjectModal();
    }, 700);
  }

  function boot() {
    if (!window.frappe || !frappe.ui || !frappe.ui.form) return setTimeout(boot, 250);
    install();
  }

  boot();
})();
