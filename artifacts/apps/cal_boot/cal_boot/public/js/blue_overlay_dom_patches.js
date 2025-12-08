// /home/frappe/frappe-bench/apps/cal_boot/cal_boot/public/js/blue_overlay_dom_patches.js
(function () {
  try {
    // نسخه‌ی فعلی
    var VERSION = 42;
    window.__BLUE_OVERLAY_DOM_PATCHES = VERSION;

    // ترجمه‌های دستیِ مطمئن (ماژول‌ها، کارت‌های هزینه و …)
    var STATIC_OVERRIDES = {
      "Human Resource": "منابع انسانی",
      "Human Resources": "منابع انسانی",
      "Expense Claims": "درخواست‌های هزینه",
      "Payroll": "حقوق و دستمزد",
      "Employee Lifecycle": "چرخهٔ حیات کارمند",
      "Attendance": "حضور و غیاب",
      "Project": "پروژه",
      "Selling": "فروش",
      "Stock": "انبار",
      "Accounts": "حسابداری",
      "Buying": "خرید",
      "CRM": "مدیریت ارتباط با مشتری",
      "Asset": "دارایی‌ها",
      "Assets": "دارایی‌ها",
      "Manufacturing": "تولید",

      "Expense Claims (this month)": "درخواست‌های هزینه (این ماه)",
      "Approved Claims (this month)": "درخواست‌های هزینهٔ تأییدشده (این ماه)",
      "Rejected Claims (this month)": "درخواست‌های هزینهٔ ردشده (این ماه)"
    };

    function hasPersian(str) {
      return /[\u0600-\u06FF]/.test(str || "");
    }

    var cache = Object.create(null);

    function translateLabel(text) {
      text = (text || "").trim();
      if (!text) return null;
      if (hasPersian(text)) return null;
      if (text.length < 2) return null;
      if (text.length > 80) return null;
      if (/^[0-9.,:%()\-\s/]+$/.test(text)) return null;

      // اول از مپ دستی استفاده کن
      if (Object.prototype.hasOwnProperty.call(STATIC_OVERRIDES, text)) {
        return STATIC_OVERRIDES[text];
      }

      if (Object.prototype.hasOwnProperty.call(cache, text)) {
        return cache[text];
      }

      var out = null;
      try {
        if (typeof __ === "function") {
          var t = __(text);
          if (t && t !== text && hasPersian(t)) {
            out = (t || "").trim();
          }
        }
      } catch (e) {
        // ignore
      }

      cache[text] = out;
      return out;
    }

    // --------- پچ براساس سلکتور برای جاهای حساس (منوها، کارت‌ها، لیست‌ها) ---------

    function patchBySelector(root, selector, label) {
      if (!root || root.nodeType !== 1) return 0;
      var els = root.querySelectorAll(selector);
      var count = 0;

      els.forEach(function (el) {
        var current = (el.innerText || el.textContent || "").trim();
        if (!current) return;

        var tr = translateLabel(current);
        if (!tr || tr === current) return;

        if (el.innerText !== undefined) el.innerText = tr;
        else el.textContent = tr;

        count++;
      });

      if (count && window.console && console.log) {
        console.log("BLUE_OVERLAY_DOM_PATCHES sel:", label || selector, "=>", count);
      }
      return count;
    }

    function runSelectorPatches(root) {
      var total = 0;

      // منوهای آبشاری (از جمله منوی داشبوردها)
      total += patchBySelector(
        root,
        ".modules-dropdown-menu .dropdown-item," +
          ".navbar .modules-dropdown-menu a.dropdown-item," +
          ".dropdown-menu .dropdown-item",
        "dropdown-items"
      );

      // عناوین Workspace و ماژول‌ها در سایدبار
      total += patchBySelector(
        root,
        ".workspace-title, .workspace-sidenav .sidebar-item .item-label",
        "workspace-titles"
      );

      // عنوان کارت‌های عددی و چارت‌ها در داشبورد
      total += patchBySelector(
        root,
        ".widget .widget-head .widget-title," +
          ".widget .card-title," +
          ".number-widget-box .number-label",
        "dashboard-widgets"
      );

      // سلول‌های لیست‌ویو (گزارش‌ها، داشبوردها، …)
      total += patchBySelector(
        root,
        ".list-view-container .list-row .list-row-col," +
          ".list-sidebar .list-link," +
          ".list-row .subject-cell",
        "list-cells"
      );

      // گزینه‌های select (فیلترها و …)
      total += patchBySelector(root, "select option", "select-options");

      return total;
    }

    // --------- پچ عمومی روی TextNode ها (fallback) ---------

    function patchTextNodes(root) {
      if (!root || root.nodeType !== 1) return 0;

      var forbiddenTags = { SCRIPT: 1, STYLE: 1, NOSCRIPT: 1 };
      if (forbiddenTags[root.nodeName]) return 0;

      var count = 0;
      var walker = document.createTreeWalker(
        root,
        NodeFilter.SHOW_TEXT,
        {
          acceptNode: function (node) {
            var txt = (node.nodeValue || "").trim();
            if (!txt) return NodeFilter.FILTER_REJECT;
            if (hasPersian(txt)) return NodeFilter.FILTER_REJECT;
            if (txt.length > 80) return NodeFilter.FILTER_REJECT;
            if (/^[0-9.,:%()\-\s/]+$/.test(txt)) return NodeFilter.FILTER_REJECT;

            var p = node.parentNode;
            if (!p) return NodeFilter.FILTER_REJECT;
            if (forbiddenTags[p.nodeName]) return NodeFilter.FILTER_REJECT;
            if (p.closest && p.closest("[data-no-blue-patch]")) {
              return NodeFilter.FILTER_REJECT;
            }
            return NodeFilter.FILTER_ACCEPT;
          }
        },
        false
      );

      var node;
      while ((node = walker.nextNode())) {
        var original = node.nodeValue || "";
        var trimmed = original.trim();
        if (!trimmed) continue;

        var tr = translateLabel(trimmed);
        if (!tr || tr === trimmed) continue;

        // فقط قسمت trim شده را جایگزین کن تا فاصله‌های دو طرف حفظ شود
        node.nodeValue = original.replace(trimmed, tr);
        count++;
        if (count <= 40 && window.console && console.log) {
          console.log("[BLUE_PATCH_TXT]", trimmed, "=>", tr);
        }
      }

      return count;
    }

    // --------- ران اصلی ---------

    function runPatches(root) {
      root = root || document.body || document.documentElement;
      if (!root) return 0;

      var total = 0;
      try {
        total += runSelectorPatches(root);
        total += patchTextNodes(root);
      } catch (e) {
        if (window.console && console.warn) {
          console.warn("BLUE_OVERLAY_DOM_PATCHES run error", e);
        }
      }

      window.__BLUE_OVERLAY_LAST_COUNT = total;
      if (window.console && console.log) {
        console.log("BLUE_OVERLAY_DOM_PATCHES walk; patched =", total);
      }
      return total;
    }

    // برای تست دستی در کنسول
    window.__BLUE_OVERLAY_RUN = function () {
      return runPatches();
    };

    // --------- اجرای اولیه ---------

    function initialRun() {
      runPatches();
    }

    if (
      document.readyState === "complete" ||
      document.readyState === "interactive"
    ) {
      initialRun();
    } else {
      document.addEventListener("DOMContentLoaded", initialRun);
    }

    // --------- after_ajax در Frappe ---------

    function scheduleRoot(node) {
      if (!node) return;
      var root = node.nodeType === 1 ? node : node.parentNode;
      if (!root) return;
      dirtyRoots.add(root);
      if (pending) return;
      pending = true;
      setTimeout(function () {
        pending = false;
        var roots = Array.from(dirtyRoots);
        dirtyRoots.clear();
        roots.forEach(function (r) {
          runPatches(r);
        });
      }, 120); // debounce برای جلوگیری از لرزش Tooltip و چارت
    }

    if (window.frappe && frappe.after_ajax) {
      frappe.after_ajax(function () {
        scheduleRoot(document.body || document.documentElement);
      });
    }

    // --------- MutationObserver با debounce ---------

    var pending = false;
    var dirtyRoots = new Set();

    if (window.MutationObserver) {
      var observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (m) {
          if (m.target) scheduleRoot(m.target);
          if (m.addedNodes) {
            m.addedNodes.forEach(function (n) {
              scheduleRoot(n);
            });
          }
        });
      });

      observer.observe(document.documentElement || document.body, {
        childList: true,
        subtree: true,
        characterData: true
      });
    }
  } catch (e) {
    if (window.console && console.error) {
      console.error("BLUE_OVERLAY_DOM_PATCHES fatal", e);
    }
  }
})();
