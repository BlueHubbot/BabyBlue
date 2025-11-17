// CAL::Desk Jalali V7 — Charts layer (Frappe Charts + Chart.js)
(() => {
  if (window.__CAL_CHARTS_V7) return; window.__CAL_CHARTS_V7 = 1;

  const isJalali = () => (localStorage.getItem("CAL_MODE") || "jalali") === "jalali";
  const havePD   = () => !!window.persianDate;

  const tryParseDate = (x) => {
    if (x == null) return null;
    if (x instanceof Date) return x;
    if (typeof x === "number") return new Date(x);
    if (typeof x === "string") {
      if (/^\d{4}-\d{2}-\d{2}/.test(x)) return new Date(x.replace(" ", "T"));
      const t = Date.parse(x); if (!Number.isNaN(t)) return new Date(t);
    }
    return null;
  };

  const fmtX = (x) => {
    if (!isJalali() || !havePD()) return String(x ?? "");
    const d = tryParseDate(x); if (!d) return String(x ?? "");
    return new window.persianDate(d).format("YYYY/MM/DD");
  };

  // ---------- A) Frappe Charts (global) ----------
  // Tooltip Jalali + اصلاح لیبل‌های محور X در SVG با MutationObserver
  if (window.frappe && window.frappe.Chart && !window.frappe.__CAL_PATCH_CHART) {
    const Target = window.frappe.Chart;

    function patchSvgTicks(container) {
      if (!isJalali() || !havePD() || !container) return;
      try {
        container.querySelectorAll("svg .x.axis text").forEach(el => {
          const raw = el.textContent || "";
          const f = fmtX(raw);
          if (f && f !== raw) el.textContent = f;
        });
      } catch (e) { /* no-op */ }
    }

    window.frappe.Chart = new Proxy(Target, {
      construct(target, args, newTarget) {
        // تلاش برای تزریق Jalali در Tooltip
        try {
          if (isJalali() && args.length) {
            let opts = args.length === 1 && typeof args[0] === "object" ? args[0]
                     : args.length >= 2 ? args[1] : null;
            if (opts && typeof opts === "object") {
              opts.tooltipOptions = opts.tooltipOptions || {};
              const baseX = opts.tooltipOptions.formatTooltipX;
              opts.tooltipOptions.formatTooltipX = (d, ...rest) => {
                try { return fmtX(d); } catch { return baseX ? baseX(d, ...rest) : String(d ?? ""); }
              };
            }
          }
        } catch (e) { /* no-op */ }

        const inst = Reflect.construct(target, args, newTarget);

        // Axis labels (SVG) → Jalali
        try {
          const parent = (args[0] && args[0].parent) || (inst && inst.parent) || null;
          if (parent && parent instanceof HTMLElement) {
            const obs = new MutationObserver(() => patchSvgTicks(parent));
            obs.observe(parent, { childList: true, subtree: true, characterData: true });
            setTimeout(() => patchSvgTicks(parent), 200);
          }
        } catch (e) { /* no-op */ }

        return inst;
      }
    });

    window.frappe.__CAL_PATCH_CHART = 1;
  }

  // ---------- B) Chart.js (global plugin) ----------
  if (window.Chart && Chart.register && !Chart.__CAL_JALALI_PLUGIN) {
    const jalaliPlugin = {
      id: "calJalali",
      beforeUpdate(chart) {
        if (!isJalali() || !havePD()) return;
        try {
          const scales = chart.options.scales || {};
          const ax = scales.x || scales.xAxis || null;
          if (ax) {
            ax.ticks = ax.ticks || {};
            const orig = ax.ticks.callback;
            ax.ticks.callback = function (value, index, ticks) {
              try {
                const raw = this.getLabelForValue ? this.getLabelForValue(value) : value;
                return fmtX(raw);
              } catch (e) {
                return typeof orig === "function" ? orig.call(this, value, index, ticks) : value;
              }
            };
          }
          const p = (chart.options.plugins = chart.options.plugins || {});
          const tt = (p.tooltip = p.tooltip || {});
          tt.callbacks = tt.callbacks || {};
          const origTitle = tt.callbacks.title;
          tt.callbacks.title = function (items) {
            try {
              const label = (items && items[0] && items[0].label) || "";
              return fmtX(label);
            } catch (e) {
              return typeof origTitle === "function" ? origTitle.call(this, items) : "";
            }
          };
        } catch (e) { /* no-op */ }
      }
    };
    Chart.register(jalaliPlugin);
    Chart.__CAL_JALALI_PLUGIN = 1;
  }

  window.__CAL_CHARTS_ACTIVE = 1;
})();
