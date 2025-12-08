// cal_boot/public/js/dash_labels_patch.js
(function () {
  // انگلیسی → فارسی
  const MAP_RAW = {
    // Attendance Dashboard
    "EARLY EXIT (THIS MONTH)": "خروج زودهنگام (این ماه)",
    "LATE ENTRY (THIS MONTH)": "ورود دیرهنگام (این ماه)",
    "TOTAL ABSENT (THIS MONTH)": "کل غیبت‌ها (این ماه)",
    "TOTAL PRESENT (THIS MONTH)": "کل حضورها (این ماه)",
    // Accounts dashboard - variant with "AGEING"
    "ACCOUNTS PAYABLE AGEING": "سررسید حساب‌های پرداختنی",
    "ACCOUNTS RECEIVABLE AGEING": "سررسید حساب‌های دریافتنی",
    "GL ENTRY": "ثبت دفتر کل (GL)",
    // Support / SLA / Role / Help texts
    "LEDGER HEALTH": "وضعیت سلامت دفتر کل",
    "OAUTH BEARER TOKEN": "توکن Bearer OAuth",
    "ONLY IF CREATOR": "فقط اگر ایجادکننده باشد",
    "BROWSE HELP TOPICS": "مرور موضوعات راهنما",
    "WE'RE HERE TO HELP": "ما اینجاییم تا کمک کنیم",
    // Sales Dashboard
    "ACTIVE CUSTOMERS": "مشتریان فعال",
    "ANNUAL SALES": "فروش سالانه",
    "TOP CUSTOMERS": "مشتریان برتر",
    "ITEM-WISE ANNUAL SALES": "فروش سالانه بر اساس کالا",
    "Bank Balance": "موجودی بانک",

    // Asset Dashboard
    "LOCATION-WISE ASSET VALUE": "ارزش دارایی‌ها بر اساس محل",

    // Buying Dashboard
    "ACTIVE SUPPLIERS": "تأمین‌کنندگان فعال",
    "ANNUAL PURCHASE": "خرید سالانه",
    "MATERIAL REQUEST ANALYSIS": "تحلیل درخواست‌های خرید",
    "TOP SUPPLIERS": "تأمین‌کنندگان برتر",

    // CRM Dashboard (کارت‌ها و چارت‌ها)
    "OPEN OPPORTUNITY": "فرصت‌های باز",
    "WON OPPORTUNITY": "فرصت‌های برنده‌شده (ماه گذشته)",
    "WON OPPORTUNITY (LAST 1 MONTH)": "فرصت‌های برنده‌شده (ماه گذشته)",
    "NEW OPPORTUNITY": "فرصت‌های جدید (ماه گذشته)",
    "NEW OPPORTUNITY (LAST 1 MONTH)": "فرصت‌های جدید (ماه گذشته)",
    "NEW LEAD": "سرنخ‌های جدید (ماه گذشته)",
    "NEW LEAD (LAST 1 MONTH)": "سرنخ‌های جدید (ماه گذشته)",
    "NEW LEADS": "سرنخ‌های جدید (ماه گذشته)",
    "INCOMING LEADS": "سرنخ‌های ورودی",
    "OPPORTUNITY TRENDS": "روند فرصت‌ها",
    "WON OPPORTUNITIES": "فرصت‌های برنده‌شده",
    "WON OPPORTUNITY TRENDS": "روند فرصت‌های برنده‌شده",
    "OPPORTUNITIES VIA CAMPAIGNS": "فرصت‌ها از طریق کمپین‌ها",
    "TERRITORY WISE OPPORTUNITY COUNT": "تعداد فرصت‌ها به تفکیک قلمرو",

    // Manufacturing Dashboard
    "MONTHLY QUALITY INSPECTION": "بازرسی کیفیت ماهانه",
    "ONGOING JOB CARD": "کارت‌های کار در حال انجام",
    "MONTHLY COMPLETED WORK ORDER": "سفارش‌های تولید تکمیل‌شده ماهانه",
    "MONTHLY TOTAL WORK ORDER": "مجموع سفارش‌های تولید ماهانه",

    // Stock / Inventory Dashboard
    "GOODS IN TRANSIT - BAD": "کالا در حال حمل - بد",
    "WORK IN PROGRESS - BAD": "کالای در جریان ساخت - بد",
    "STORES - BAD": "انبارها - بد",
    "FINISHED GOODS - BAD": "کالای ساخته‌شده - بد",
    "DELIVERY TRENDS": "روند تحویل‌ها",
    "PURCHASE RECEIPT TRENDS": "روند رسیدهای خرید",
    "ITEM SHORTAGE SUMMARY": "خلاصه کمبود کالا",
    "OLDEST ITEMS": "قدیمی‌ترین اقلام",

    // Human Resource Dashboard
    "NEW HIRES (THIS YEAR)": "استخدام‌های جدید (امسال)",
    "TOTAL EMPLOYEES": "کل کارکنان",

    // Expense Claims Dashboard
    "REJECTED CLAIMS (THIS MONTH)": "درخواست‌های ردشده (این ماه)",
    "APPROVED CLAIMS (THIS MONTH)": "درخواست‌های تأییدشده (این ماه)",
    "EXPENSE CLAIMS (THIS MONTH)": "درخواست‌های هزینه (این ماه)",

    // Recruitment Dashboard
    "REJECTED JOB APPLICANTS": "متقاضیان شغل ردشده",
    "ACCEPTED JOB APPLICANTS": "متقاضیان شغل پذیرفته‌شده",
    "TOTAL APPLICANTS (THIS MONTH)": "کل متقاضیان (این ماه)",
    "JOB OFFER ACCEPTANCE RATE": "نرخ پذیرش پیشنهاد شغلی",
    "APPLICANT-TO-HIRE PERCENTAGE": "درصد تبدیل متقاضی به استخدام",
    "JOB OFFERS (THIS MONTH)": "پیشنهادهای شغلی (این ماه)",

    // Employee Lifecycle Dashboard
    "TRANSFERS (THIS MONTH)": "انتقال‌ها (این ماه)",
    "PROMOTIONS (THIS MONTH)": "ارتقاها (این ماه)",
    "SEPARATIONS (THIS MONTH)": "قطع همکاری‌ها (این ماه)",
    "ONBOARDINGS (THIS MONTH)": "استخدام‌های جدید (این ماه)",
    "TRAININGS (THIS MONTH)": "آموزش‌ها (این ماه)",

    // Payroll Dashboard
    "TOTAL OUTGOING SALARY(LAST MONTH)": "کل حقوق پرداختی (ماه گذشته)",
    "TOTAL INCENTIVE GIVEN(LAST MONTH)": "کل پاداش پرداختی (ماه گذشته)",
    "TOTAL SALARY STRUCTURE": "مجموع ساختارهای حقوق و دستمزد",
    "TOTAL DECLARATION SUBMITTED": "کل اظهارنامه‌های ثبت‌شده",
    "DEPARTMENT WISE SALARY(LAST MONTH)": "حقوق بر اساس دپارتمان (ماه گذشته)",
    "DESIGNATION WISE SALARY(LAST MONTH)": "حقوق بر اساس سمت (ماه گذشته)",

    // Accounts Dashboard / Reports
    "OUTGOING BILLS (SALES INVOICE)": "صورت‌حساب‌های خروجی (فاکتور فروش)",
    "INCOMING BILLS (PURCHASE INVOICE)": "صورت‌حساب‌های ورودی (فاکتور خرید)",
    "ACCOUNTS PAYABLE AGING": "سررسید حساب‌های پرداختنی",
    "ACCOUNTS RECEIVABLE AGING": "سررسید حساب‌های دریافتنی",
    "BUDGET VARIANCE": "انحراف از بودجه",

    // Workspace menu
    "HUMAN RESOURCE": "منابع انسانی",
    "EXPENSE CLAIMS": "درخواست‌های هزینه",
    "RECRUITMENT": "استخدام",
    "PAYROLL": "حقوق و دستمزد",
    "EMPLOYEE LIFECYCLE": "چرخه حیات کارمند",
    "ATTENDANCE": "حضور و غیاب",
    "PROJECT": "پروژه",
    "SELLING": "فروش",
    "STOCK": "انبار",
    "ACCOUNTS": "حسابداری",
    "BUYING": "خرید",
    "CRM": "مدیریت ارتباط با مشتری",
    "ASSET": "دارایی‌ها",
    "MANUFACTURING": "تولید",
  };

  function canon(s) {
    return s
      .replace(/\s+/g, " ")
      .replace(/\s+\)/g, ")")
      .replace(/\(\s+/g, "(")
      .trim()
      .toUpperCase();
  }

  const MAP = {};
  Object.keys(MAP_RAW).forEach((k) => {
    MAP[canon(k)] = MAP_RAW[k];
  });

  function patchNodeText(el) {
    if (!el) return;
    const text = (el.innerText || "").trim();
    if (!text) return;
    const fa = MAP[canon(text)];
    if (fa && text !== fa) {
      el.innerText = fa;
    }
  }

  function patchAll(root) {
    if (!root || !root.querySelectorAll) return;
    const container =
      root.querySelector(".page-container, .desk-container") || root;

    const nodes = container.querySelectorAll(
      ".widget .widget-head .widget-title, " + // عنوان ویجت‌ها
      ".number-card, .number-card-title, " +  // کارت‌های عددی
      "button, div, span, a, h1, h2, h3, th"  // عمومی
    );
    nodes.forEach(patchNodeText);
  }

  function boot() {
    if (!document.body) return;

    // پچ اولیه
    patchAll(document);

    // تایمر دائم: هر ۷۰۰ms یک‌بار کل صفحه را پچ می‌کند
    setInterval(() => {
      patchAll(document);
    }, 700);

    // MutationObserver برای نودهای جدید و تغییر متن
    const obs = new MutationObserver((mutations) => {
      for (const m of mutations) {
        if (m.type === "characterData") {
          patchNodeText(m.target.parentElement || m.target);
        } else if (m.type === "childList") {
          m.addedNodes.forEach((node) => {
            if (node.nodeType === 1) {
              patchAll(node);
            }
          });
        }
      }
    });
    obs.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
