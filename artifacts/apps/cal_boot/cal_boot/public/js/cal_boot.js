// apps/cal_boot/cal_boot/public/js/cal_boot.js
// CAL Boot – Jalali/Gregorian switch + BlueJalaliPicker/Range +
// Jalali display layer on inputs + Jalali labels on charts (axes + tooltips)

(function () {
  "use strict";

  var w = window;
  var d = document;
  var CAL = w.CAL = w.CAL || {};
  var MODE_KEY = "__CAL_MODE__";

  // ---- simple logger ----
  function log() {
    if (!w.console || !console.log) return;
    var args = Array.prototype.slice.call(arguments);
    args.unshift("[CAL]");
    console.log.apply(console, args);
  }

  // ==== calendar mode (jalali / gregorian) ====

  CAL.getMode = function () {
    try {
      return localStorage.getItem(MODE_KEY) || "gregorian";
    } catch (e) {
      return "gregorian";
    }
  };

  CAL.setMode = function (mode) {
    mode = mode === "jalali" ? "jalali" : "gregorian";
    try {
      localStorage.setItem(MODE_KEY, mode);
    } catch (e) {}

    var ev;
    try {
      ev = new CustomEvent("CAL_MODE_CHANGE", { detail: { mode: mode } });
    } catch (err) {
      ev = d.createEvent("CustomEvent");
      ev.initCustomEvent("CAL_MODE_CHANGE", true, true, { mode: mode });
    }
    w.dispatchEvent(ev);
    updateToggleLabel();
  };

  CAL.isJalali = function () {
    return CAL.getMode() === "jalali";
  };

  // ==== navbar toggle button ====

  var toggleBtn = null;

  function updateToggleLabel() {
    if (!toggleBtn) return;
    var mode = CAL.getMode();
    toggleBtn.textContent = mode === "jalali"
      ? "تقویم: شمسی"
      : "تقویم: میلادی";
  }

  function ensureHeaderToggle() {
    if (toggleBtn && d.body.contains(toggleBtn)) {
      updateToggleLabel();
      return;
    }

    var navbar =
      d.querySelector(".navbar .navbar-collapse") ||
      d.querySelector(".navbar");

    if (!navbar) {
      setTimeout(ensureHeaderToggle, 500);
      return;
    }

    var container =
      navbar.querySelector(".navbar-right") ||
      navbar.lastElementChild ||
      navbar;

    toggleBtn = d.createElement("button");
    toggleBtn.type = "button";
    toggleBtn.className = "btn btn-default btn-xs cal-mode-toggle";
    toggleBtn.style.marginLeft = "8px";
    toggleBtn.style.marginRight = "8px";

    toggleBtn.onclick = function (e) {
      e.preventDefault();
      var newMode = CAL.isJalali() ? "gregorian" : "jalali";
      CAL.setMode(newMode);
    };

    updateToggleLabel();

    var searchBar = d.querySelector(".navbar .search, .navbar .form-inline");
    if (searchBar && searchBar.parentNode) {
      searchBar.parentNode.insertBefore(toggleBtn, searchBar.nextSibling);
    } else {
      container.appendChild(toggleBtn);
    }
  }

  // ==== helpers: inside Blue calendars? ====

  function isInsideBlueCalendars(target) {
    if (!target) return false;
    var singleRoot = d.getElementById("blue-jalali-picker-root");
    if (singleRoot && singleRoot.contains(target)) return true;
    var rangeRoot = d.getElementById("blue-jalali-range-root");
    if (rangeRoot && rangeRoot.contains(target)) return true;
    return false;
  }

  // ==== resolve actual input from event ====

  function resolveInputTarget(ev) {
    var t = ev.target;
    if (!t) return null;

    if (t.tagName === "INPUT") return t;

    var input = t.closest && t.closest("input");
    if (input) return input;

    var wrapper = t.closest && t.closest(
      ".date-range, .control-input, .frappe-control, .filter-field, .input-with-feedback, .form-group, .control-input-wrapper"
    );
    if (wrapper) {
      input = wrapper.querySelector("input");
      if (input) return input;
    }

    return null;
  }

  // ==== detect single Date input ====

  function isDateInput(el) {
    if (!el || el.tagName !== "INPUT") return false;

    // 1) مستقیم روی خود input
    var ft = (el.getAttribute("data-fieldtype") || "").toLowerCase();
    if (ft === "date" || ft === "datetime") return true;

    if (
      el.classList.contains("date-field") ||
      el.classList.contains("datepicker-input") ||
      el.classList.contains("date")
    ) {
      return true;
    }

    // 2) wrapper با data-fieldtype (فیلترهای چارت / داشبورد)
    var wrapper = el.closest && el.closest("[data-fieldtype]");
    if (wrapper) {
      var wft = (wrapper.getAttribute("data-fieldtype") || "").toLowerCase();
      if (wft === "date" || wft === "datetime") {
        return true;
      }
    }

    if (el.hasAttribute("data-blue-nojalali")) return false;

    return false;
  }

  // ==== detect DateRange input ====

  function isRangeInput(el) {
    if (!el || el.tagName !== "INPUT") return false;

    var ftRaw =
      el.getAttribute("data-fieldtype") ||
      el.getAttribute("data-type") ||
      "";
    var ft = ftRaw.toLowerCase();

    // 1) مستقیم روی خود input
    if (ft === "daterange" || ft === "date range") return true;
    if (ft.indexOf("date") !== -1 && ft.indexOf("range") !== -1) return true;

    if (
      el.classList.contains("date-range") ||
      el.classList.contains("date-range-field") ||
      el.classList.contains("daterange-input") ||
      el.classList.contains("frappe-date-range")
    ) {
      return true;
    }

    // 2) wrapper با data-fieldtype (فیلترهای چارت / داشبورد)
    var wrapper = el.closest && el.closest("[data-fieldtype]");
    if (wrapper) {
      var wft = (wrapper.getAttribute("data-fieldtype") || "").toLowerCase();
      if (
        wft === "daterange" ||
        wft === "date range" ||
        (wft.indexOf("date") !== -1 && wft.indexOf("range") !== -1)
      ) {
        return true;
      }
    }

    if (el.hasAttribute("data-blue-nojalali-range")) return false;

    return false;
  }

  // ==== BlueJalaliPicker / BlueJalaliRange instances ====

  function ensureBluePickerInstance() {
    return new Promise(function (resolve, reject) {
      if (!w.BlueJalaliPicker) {
        return reject(new Error("BlueJalaliPicker missing on window"));
      }
      if (!w.__BLUE_PICKER) {
        w.__BLUE_PICKER = new w.BlueJalaliPicker({
          onSelect: function (info) {
            log("BlueJalaliPicker select", info.gregorian, info.jalali);
          }
        });
      }
      resolve(w.__BLUE_PICKER);
    });
  }

  function ensureBlueRangeInstance() {
    return new Promise(function (resolve, reject) {
      if (!w.BlueJalaliRangePicker) {
        return reject(new Error("BlueJalaliRangePicker missing on window"));
      }
      if (!w.__BLUE_RANGE_PICKER) {
        w.__BLUE_RANGE_PICKER = new w.BlueJalaliRangePicker({});
      }
      resolve(w.__BLUE_RANGE_PICKER);
    });
  }

  // ==== Jalali display overlay helpers (inputs) ====

  function ensureDisplayCss() {
    if (d.getElementById("cal-display-css")) return;
    var style = d.createElement("style");
    style.id = "cal-display-css";
    style.type = "text/css";
    style.textContent = `
.cal-date-display {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2;
  pointer-events: none;
  display: flex;
  align-items: center;
  padding: 0 8px;
  font-size: inherit;
  font-weight: inherit;
  color: #111827;
  direction: ltr;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
    `.trim();
    d.head.appendChild(style);
  }

  function getInputWrapper(input) {
    if (!input) return null;

    var wrapper = null;

    if (input.closest) {
      wrapper = input.closest(
        ".frappe-control, .form-group, .control-input-wrapper, .filter-field, .control-input, .date-range"
      );
    }

    if (!wrapper || wrapper === input) {
      wrapper = input.parentElement || null;
    }

    return wrapper;
  }

  function gregStrToJalaliStr(g) {
    if (!g || !/^\d{4}-\d{2}-\d{2}$/.test(g)) return g || "";
    if (!w.persianDate) return g;
    try {
      var p = g.split("-");
      var gy = parseInt(p[0], 10);
      var gm = parseInt(p[1], 10) - 1;
      var gd = parseInt(p[2], 10);
      var dt = new Date(gy, gm, gd, 12, 0, 0, 0);
      var unix = dt.getTime();
      if (!isFinite(unix)) return g;
      var pd = new w.persianDate(unix).toCalendar("persian").toLocale("en");
      return pd.format("YYYY-MM-DD");
    } catch (e) {
      console.error("[CAL] gregStrToJalaliStr error:", e);
      return g;
    }
  }

   // ==== charts: axis & tooltip Jalali patch ====

  // فلگ برای جلوگیری از لوپ در MutationObserver
  w.__CAL_PATCHING_CHARTS__ = false;

  // تبدیل لیبل محور/tooltip به جلالی (اگر لازم باشد)
  function convertChartLabel(orig, mode) {
    if (!orig) return orig;
    if (mode !== "jalali") return orig;

    // حالت ۱: تاریخ روز دقیق YYYY-MM-DD
    if (/^\d{4}-\d{2}-\d{2}$/.test(orig)) {
      return gregStrToJalaliStr(orig);
    }

    // حالت ۲: سال-ماه YYYY-MM  → اول ماه
    var mYM = orig.match(/^(\d{4})-(\d{2})$/);
    if (mYM) {
      return gregStrToJalaliStr(mYM[1] + "-" + mYM[2] + "-01").slice(0, 7); // 1404-09
    }

    // حالت ۳: MonthName YYYY مثل "Dec 2025" یا "Jan 2025"
    var parts = orig.split(/\s+/);
    if (parts.length === 2) {
      var name = parts[0];
      var year = parseInt(parts[1], 10);

      if (year && year > 1900 && year < 2100) {
        var key = name.substr(0, 3).toLowerCase(); // Dec → dec, December → dec
        var idxMap = {
          jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5,
          jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11
        };

        if (idxMap.hasOwnProperty(key)) {
          try {
            // وسط ماه را می‌گیریم که مطمئن باشیم در بازه است
            var dt = new Date(year, idxMap[key], 15);
            var unix = dt.getTime();
            if (isFinite(unix) && w.persianDate) {
              var pd = new w.persianDate(unix)
                .toCalendar("persian")
                .toLocale("en");
              // فقط سال-ماه جلالی (اعداد لاتین)
              return pd.format("YYYY-MM"); // مثلاً 1403-09
            }
          } catch (e) {
            console.error("[CAL] convertChartLabel month-name error:", e);
          }
        }
      }
    }

    // بقیه فرمت‌ها (مثلاً "2025-2026" یا چیزهای خاص) را فعلاً دست نمی‌زنیم
    return orig;
  }

  CAL.patchCharts = function (root) {
    root = root || d;

    if (w.__CAL_PATCHING_CHARTS__) return;
    w.__CAL_PATCHING_CHARTS__ = true;

    try {
      var mode = CAL.getMode();

      // محور X
      var axisTexts = root.querySelectorAll("svg.chart .x.axis text");
      axisTexts.forEach(function (el) {
        var orig = el.getAttribute("data-cal-orig-label");
        if (!orig) {
          orig = (el.textContent || "").trim();
          if (!orig) return;
          el.setAttribute("data-cal-orig-label", orig);
        }
        var newLabel = convertChartLabel(orig, mode);
        el.textContent = newLabel;
      });

      // tooltip (گراف SVG → .graph-svg-tip .title)
      var titles = root.querySelectorAll(".graph-svg-tip .title");
      titles.forEach(function (el) {
        var orig = el.getAttribute("data-cal-orig-label");
        var textNode;

        if (el.childNodes && el.childNodes.length > 0 && el.childNodes[0].nodeType === 3) {
          textNode = el.childNodes[0];
        } else {
          textNode = el;
        }

        if (!orig) {
          orig = (textNode.textContent || "").trim();
          if (!orig) return;
          el.setAttribute("data-cal-orig-label", orig);
        }

        var newLabel = convertChartLabel(orig, mode);
        textNode.textContent = newLabel;
      });
    } catch (e) {
      console.error("[CAL] patchCharts error:", e);
    } finally {
      w.__CAL_PATCHING_CHARTS__ = false;
    }
  };

  function observeCharts() {
    if (d.__calChartsObserved) return;
    d.__calChartsObserved = true;

    try {
      var scheduled = false;

      var observer = new MutationObserver(function (mutations) {
        // اگر خودمان داریم patch می‌کنیم، تغییراتش را نادیده بگیر
        if (w.__CAL_PATCHING_CHARTS__) return;

        var need = false;
        for (var i = 0; i < mutations.length; i++) {
          var m = mutations[i];
          if (m.type === "childList" || m.type === "characterData") {
            need = true;
            break;
          }
        }
        if (!need) return;

        if (scheduled) return;
        scheduled = true;

        // throttle: حداکثر هر 30ms یک بار patch
        setTimeout(function () {
          scheduled = false;
          try {
            CAL.patchCharts();
          } catch (e) {
            console.error("[CAL] patchCharts (throttled) error:", e);
          }
        }, 30);
      });

      observer.observe(d.body, {
        childList: true,
        subtree: true,
        characterData: true
      });

      d.__calChartsObserver = observer;
    } catch (e) {
      console.error("[CAL] observeCharts error:", e);
    }
  }


  // ==== Jalali display overlay for inputs ====

  CAL.refreshDisplayForInput = function (input) {
    if (!input || input.tagName !== "INPUT") return;

    var isDate = isDateInput(input);
    var isRange = isRangeInput(input);

    // not a date/daterange → remove overlay if any
    if (!isDate && !isRange) {
      if (input.__calDisplayEl && input.__calDisplayEl.parentNode) {
        input.__calDisplayEl.parentNode.removeChild(input.__calDisplayEl);
      }
      if (input.__calOrigStyle) {
        input.style.color = input.__calOrigStyle.color;
        input.style.caretColor = input.__calOrigStyle.caretColor;
      } else {
        input.style.color = "";
        input.style.caretColor = "";
      }
      return;
    }

    // gregorian mode → remove overlay
    if (!CAL.isJalali()) {
      if (input.__calDisplayEl && input.__calDisplayEl.parentNode) {
        input.__calDisplayEl.parentNode.removeChild(input.__calDisplayEl);
      }
      if (input.__calOrigStyle) {
        input.style.color = input.__calOrigStyle.color;
        input.style.caretColor = input.__calOrigStyle.caretColor;
      } else {
        input.style.color = "";
        input.style.caretColor = "";
      }
      return;
    }

    // jalali mode: create/update overlay
    ensureDisplayCss();

    var wrapper = getInputWrapper(input);
    if (!wrapper) return;

    var span = input.__calDisplayEl;
    if (!span || !wrapper.contains(span)) {
      span = d.createElement("div");
      span.className = "cal-date-display";
      wrapper.appendChild(span);
      input.__calDisplayEl = span;
    }

    if (!input.__calOrigStyle) {
      input.__calOrigStyle = {
        color: input.style.color || "",
        caretColor: input.style.caretColor || ""
      };
    }

    var raw = (input.value || "").trim();
    var displayText = "";

    if (!raw) {
      displayText = input.getAttribute("placeholder") || "";
    } else if (isRange) {
      // DateRange – فرمت‌های مختلف:
      // 1) "YYYY-MM-DD - YYYY-MM-DD"
      // 2) "YYYY-MM-DD,YYYY-MM-DD"
      // 3) حداقل دو تاریخ میلادی با جداکننده‌ی فاصله/کاما
      var from = null;
      var to = null;

      var m1 = raw.match(/^(\d{4}-\d{2}-\d{2})\s*[-–]\s*(\d{4}-\d{2}-\d{2})$/);
      if (m1) {
        from = m1[1];
        to = m1[2];
      } else {
        var m2 = raw.match(/^(\d{4}-\d{2}-\d{2})\s*,\s*(\d{4}-\d{2}-\d{2})$/);
        if (m2) {
          from = m2[1];
          to = m2[2];
        } else {
          var parts = raw.split(/[,\s]+/).filter(Boolean);
          if (
            parts.length >= 2 &&
            /^\d{4}-\d{2}-\d{2}$/.test(parts[0]) &&
            /^\d{4}-\d{2}-\d{2}$/.test(parts[1])
          ) {
            from = parts[0];
            to = parts[1];
          }
        }
      }

      if (from && to) {
        var j1 = gregStrToJalaliStr(from);
        var j2 = gregStrToJalaliStr(to);
        displayText = j1 + " - " + j2;
      } else {
        displayText = raw;
      }
    } else if (isDate) {
      displayText = gregStrToJalaliStr(raw);
    } else {
      displayText = raw;
    }

    span.textContent = displayText;

    try {
      var cs = w.getComputedStyle(input);
      span.style.fontSize = cs.fontSize;
      span.style.fontWeight = cs.fontWeight;
      span.style.paddingLeft = cs.paddingLeft;
      span.style.paddingRight = cs.paddingRight;

      var ta = cs.textAlign;
      if (ta === "right") {
        span.style.justifyContent = "flex-end";
      } else if (ta === "center") {
        span.style.justifyContent = "center";
      } else {
        span.style.justifyContent = "flex-start";
      }

      var wcs = w.getComputedStyle(wrapper);
      if (wcs.position === "static") {
        wrapper.style.position = "relative";
      }
    } catch (e) {}

    input.style.color = "transparent";
    input.style.caretColor = "transparent";
  };

  CAL.refreshAllDisplays = function () {
    var inputs = Array.prototype.slice.call(d.querySelectorAll("input"));
    inputs.forEach(function (el) {
      if (isDateInput(el) || isRangeInput(el)) {
        CAL.refreshDisplayForInput(el);
      }
    });
  };

  // ==== Frappe control resolution ====

  function getFrappeControlForInput(input) {
    if (!input) return null;

    try {
      if (input._control) {
        return input._control;
      }
    } catch (e) {}

    var fieldname =
      input.getAttribute("data-fieldname") ||
      input.name ||
      null;

    var wrapper = input.closest && input.closest(
      ".frappe-control, .form-group, .filter-field, .control-input-wrapper"
    );

    if (!fieldname && wrapper) {
      if (wrapper.dataset && wrapper.dataset.fieldname) {
        fieldname = wrapper.dataset.fieldname;
      } else {
        fieldname =
          wrapper.getAttribute("data-fieldname") ||
          wrapper.getAttribute("data-fieldname") ||
          null;
      }
    }

    var ctrl = null;

    try {
      if (!ctrl && w.cur_frm && cur_frm.fields_dict && fieldname && cur_frm.fields_dict[fieldname]) {
        ctrl = cur_frm.fields_dict[fieldname];
      }
    } catch (e) {}

    try {
      if (!ctrl && w.cur_page && cur_page.page && cur_page.page.fields_dict && fieldname && cur_page.page.fields_dict[fieldname]) {
        ctrl = cur_page.page.fields_dict[fieldname];
      }
    } catch (e) {}

    return ctrl;
  }

  function syncFrappeControlFromInput(input, range) {
    var ctrl = getFrappeControlForInput(input);
    if (!ctrl) return;

    var val = range.from_greg + " - " + range.to_greg;

    try {
      if (typeof ctrl.set_value === "function") {
        ctrl.set_value(val);
        return;
      }

      if (ctrl.$input && ctrl.$input[0] === input && w.jQuery) {
        ctrl.$input.val(val).trigger("change");
        return;
      }
    } catch (e) {
      console.error("[CAL] syncFrappeControlFromInput error:", e);
    }
  }

  // ==== bridge to native datepicker (for reports / charts) ====

  function callNativeRangeCallback(input, range) {
    if (!input) return;

    var dp = null;

    try {
      if (input._datepicker) {
        dp = input._datepicker;
      } else if (input._airDatepicker) {
        dp = input._airDatepicker;
      } else if (input.adp) {
        dp = input.adp;
      } else if (w.jQuery) {
        var $ = w.jQuery;
        dp =
          $(input).data("datepicker") ||
          $(input).data("airDatepicker") ||
          $(input).data("dateRangePicker") ||
          null;
      }
    } catch (e) {
      console.error("[CAL] find native datepicker failed:", e);
    }

    if (!dp) {
      return;
    }

    var fromDate, toDate;
    try {
      fromDate = new Date(range.from_greg);
      toDate = new Date(range.to_greg);
    } catch (e) {
      console.error("[CAL] invalid range dates for native dp:", e);
      return;
    }

    try {
      if (typeof dp.selectDate === "function") {
        dp.selectDate([fromDate, toDate]);
        return;
      }
    } catch (e) {
      console.error("[CAL] dp.selectDate error:", e);
    }

    try {
      if (dp.opts && typeof dp.opts.onSelect === "function") {
        dp.opts.onSelect({
          date: [fromDate, toDate],
          formattedDate: [range.from_greg, range.to_greg],
          datepicker: dp
        });
      }
    } catch (e) {
      console.error("[CAL] native onSelect call error:", e);
    }
  }

  // ==== global handler: single Date ====

  function globalDateHandler(ev) {
    if (isInsideBlueCalendars(ev.target)) return;

    if (!CAL.isJalali()) return;

    var t = resolveInputTarget(ev);
    if (!t || t.tagName !== "INPUT") return;

    if (isRangeInput(t)) return;

    if (!isDateInput(t)) return;

    if (ev.type === "mousedown" && ev.button !== 0) return;

    ev.preventDefault();
    ev.stopPropagation();
    if (ev.stopImmediatePropagation) ev.stopImmediatePropagation();

    ensureBluePickerInstance()
      .then(function (picker) {
        picker.open(t, t.value);
      })
      .catch(function (err) {
        console.error("[CAL] BlueJalaliPicker error:", err);
      });
  }

  // ==== global handler: DateRange ====

  function globalRangeHandler(ev) {
    if (isInsideBlueCalendars(ev.target)) return;

    if (!CAL.isJalali()) return;

    var input = resolveInputTarget(ev);
    if (!input || input.tagName !== "INPUT") return;
    if (!isRangeInput(input)) return;

    ev.preventDefault();
    ev.stopPropagation();
    if (ev.stopImmediatePropagation) ev.stopImmediatePropagation();

    if (ev.type !== "click" && ev.type !== "focus") {
      return;
    }

    var raw = (input.value || "").trim();
    var from = null;
    var to = null;

    if (raw) {
      // پشتیبانی از "from - to"، "from,to" و حالت‌های مشابه
      var m1 = raw.match(/^(\d{4}-\d{2}-\d{2})\s*[-–]\s*(\d{4}-\d{2}-\d{2})$/);
      if (m1) {
        from = m1[1];
        to = m1[2];
      } else {
        var m2 = raw.match(/^(\d{4}-\d{2}-\d{2})\s*,\s*(\d{4}-\d{2}-\d{2})$/);
        if (m2) {
          from = m2[1];
          to = m2[2];
        } else {
          var parts = raw.split(/[,\s]+/).filter(Boolean);
          if (
            parts.length >= 2 &&
            /^\d{4}-\d{2}-\d{2}$/.test(parts[0]) &&
            /^\d{4}-\d{2}-\d{2}$/.test(parts[1])
          ) {
            from = parts[0];
            to = parts[1];
          }
        }
      }
    }

    ensureBlueRangeInstance()
      .then(function (picker) {
        if (picker.isOpen && picker.anchor === input) {
          return;
        }

        picker.opts.onSelect = function (range) {
          var val = range.from_greg + " - " + range.to_greg;

          var usedControl = false;
          try {
            var ctrl = getFrappeControlForInput(input);
            if (ctrl && typeof ctrl.set_value === "function") {
              ctrl.set_value(val);
              usedControl = true;
            }
          } catch (e) {
            console.error("[CAL] control.set_value error:", e);
          }

          if (!usedControl) {
            input.value = val;
            try {
              input.dispatchEvent(new Event("input", { bubbles: true }));
              input.dispatchEvent(new Event("change", { bubbles: true }));
            } catch (e) {
              var evt1 = d.createEvent("HTMLEvents");
              evt1.initEvent("input", true, false);
              input.dispatchEvent(evt1);
              var evt2 = d.createEvent("HTMLEvents");
              evt2.initEvent("change", true, false);
              input.dispatchEvent(evt2);
            }
          }

          try {
            callNativeRangeCallback(input, range);
          } catch (e) {
            console.error("[CAL] callNativeRangeCallback error:", e);
          }

          try {
            syncFrappeControlFromInput(input, range);
          } catch (e) {
            console.error("[CAL] syncFrappeControlFromInput error:", e);
          }

          try {
            CAL.refreshDisplayForInput(input);
          } catch (e) {}
        };

        picker.open(input, from, to);
      })
      .catch(function (err) {
        console.error("[CAL] BlueJalaliRangePicker error:", err);
      });
  }

  // ==== install global handlers ====

  function installGlobalDateHandler() {
    // single Date
    d.addEventListener("mousedown", globalDateHandler, true);
    d.addEventListener("focus", globalDateHandler, true);
    d.addEventListener("click", globalDateHandler, true);

    // DateRange
    d.addEventListener("mousedown", globalRangeHandler, true);
    d.addEventListener("focus", globalRangeHandler, true);
    d.addEventListener("click", globalRangeHandler, true);

    // keep display in sync when Frappe changes values
    d.addEventListener("change", function (e) {
      var t = resolveInputTarget(e) || e.target;
      if (!t || t.tagName !== "INPUT") return;
      if (!isDateInput(t) && !isRangeInput(t)) return;
      try {
        CAL.refreshDisplayForInput(t);
      } catch (err) {}
    }, true);
  }

  // ==== hook router for new pages ====

  function hookRouter() {
    try {
      if (w.frappe && frappe.router && frappe.router.on) {
        frappe.router.on("change", function () {
          setTimeout(function () {
            ensureHeaderToggle();
            CAL.refreshAllDisplays();
            CAL.patchCharts();
          }, 100);
        });
      }
    } catch (e) {}
  }

  // ==== init / boot ====

  function init() {
    log("desk boot init, mode =", CAL.getMode());
    ensureHeaderToggle();
    installGlobalDateHandler();
    hookRouter();
    setTimeout(function () {
      CAL.refreshAllDisplays();
      CAL.patchCharts();
      observeCharts();
    }, 50);
  }

  function boot() {
    if (CAL.ensureLibs && typeof CAL.ensureLibs === "function") {
      CAL.ensureLibs()
        .then(function () {
          init();
        })
        .catch(function (err) {
          console.error("[CAL] ensureLibs error:", err);
          init();
        });
    } else {
      init();
    }
  }

  if (d.readyState === "loading") {
    d.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  w.addEventListener("CAL_MODE_CHANGE", function (e) {
    log("mode changed:", e.detail && e.detail.mode);
    try {
      CAL.refreshAllDisplays();
      CAL.patchCharts();
    } catch (err) {}
  });

  w.__CAL_DESK_BOOT_V25 = 1;
})();
