/* BlueDocs helper – force root, never /blueapi/ */
(() => {
  // مقصد قطعی مستندات
  const DOCS = "https://docs.bluehesab.ir/";

  // اگر (به هر دلیلی) کاربر روی /blueapi/ وارد داکس شد، سمت کلاینت هم normalize کن
  if (location.hostname === "docs.bluehesab.ir" && location.pathname.startsWith("/blueapi/")) {
    const rest = location.pathname.slice("/blueapi".length); // چیزی بعد از /blueapi
    const targetPath = "/" + rest.replace(/^\/+/, "");
    // به ریشه ببر (همراه query و hash)
    location.replace(targetPath + location.search + location.hash);
    return;
  }

  // هِلپر عمومی برای باز کردن داکس از پنل
  window.BlueDocs = function (path = "") {
    const url = DOCS + String(path).replace(/^\/+/, "");
    window.open(url, "_blank", "noopener");
  };

  // اگر جایی در پنل «old global» استفاده شده بود، همین را در اختیار بگذار
  window.DOCS = DOCS;
})();
