// اول از همه: سرویس‌ورکرها و کش‌های قدیمی رو بکش بیرون
(async () => {
  try {
    if ('serviceWorker' in navigator) {
      const regs = await navigator.serviceWorker.getRegistrations();
      for (const r of regs) {
        try { await r.unregister(); } catch (e) {}
      }
    }
    if (window.caches && caches.keys) {
      const keys = await caches.keys();
      for (const k of keys) {
        try { await caches.delete(k); } catch (e) {}
      }
    }
  } catch (e) {}
})();

// از اینجا به بعد همون منوی سه‌تایی که قبلاً داشتی 👇
(function () {
  // فقط روی /app فعال باشه
  if (!/^\/app(\/|$)/.test(location.pathname)) return;

  const DOCS = "https://docs.bluehesab.ir/";
  const SUPPORT = "https://support.bluehesab.ir/help";

  const norm = s =>
    String(s || "")
      .replace(/\s+/g, " ")
      .replace(/[\u200c\u200f\u202a-\u202e]/g, "")
      .trim();

  function ensureShortcuts(menu) {
    const hasItem = [...menu.querySelectorAll("a")].some(a =>
      /میانبرهای صفحه‌کلید|Keyboard Shortcuts/i.test(norm(a.textContent))
    );
    if (hasItem) return;

    const li = document.createElement("li");
    const a = document.createElement("a");
    a.className = "dropdown-item";
    a.textContent = "میانبرهای صفحه‌کلید";
    a.href = "#";
    a.addEventListener("click", e => {
      e.preventDefault();
      try {
        if (frappe?.ui?.keys?.show_shortcuts) {
          return frappe.ui.keys.show_shortcuts();
        }
      } catch (_) {}
      document.dispatchEvent(
        new KeyboardEvent("keydown", {
          key: "?",
          code: "Slash",
          shiftKey: true,
          which: 191,
          keyCode: 191,
          bubbles: true
        })
      );
    });
    li.appendChild(a);
    menu.appendChild(li);
  }

  function rebuild() {
    const help = document.querySelector(".dropdown-help");
    const menu = help && help.querySelector(".dropdown-menu");
    if (!menu) return;

    menu.innerHTML = "";

    const mk = (txt, href) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.className = "dropdown-item";
      a.textContent = txt;
      a.href = href;
      a.target = "_blank";
      a.rel = "noopener";
      li.appendChild(a);
      return li;
    };

    menu.appendChild(mk("مستندات", DOCS));
    menu.appendChild(mk("پشتیبانی BlueAPI", SUPPORT));
    ensureShortcuts(menu);
  }

  document.addEventListener(
    "shown.bs.dropdown",
    e => {
      if (e.target?.classList?.contains("dropdown-help")) {
        setTimeout(rebuild, 0);
      }
    },
    true
  );

  let n = 0;
  const id = setInterval(() => {
    rebuild();
    if (++n > 8) clearInterval(id);
  }, 500);
})();
