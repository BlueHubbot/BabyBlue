/*! BlueAPi Overlay (rtl.js) — RTL + i18n + Homepage Sections (guarded) */
(function(){
  const ready=f=>document.readyState!=="loading"?f():document.addEventListener("DOMContentLoaded",f);
  const qs=(s,r=document)=>r.querySelector(s), qsa=(s,r=document)=>Array.from(r.querySelectorAll(s));
  function findByText(selector,texts){const list=typeof selector==="string"?qsa(selector):(selector||[]);
    const norms=(texts||[]).map(t=>String(t).normalize("NFKC").replace(/\s+/g," ").trim().toLowerCase());
    return list.find(n=>{const txt=(n.innerText||n.textContent||"").normalize("NFKC").replace(/\s+/g," ").trim().toLowerCase();
      return norms.some(x=>txt.includes(x));})||null;}
  function debounce(fn,w=200){let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>fn.apply(null,a),w);};}
  const DIGIT_MAP={"۰":"0","۱":"1","۲":"2","۳":"3","۴":"4","۵":"5","۶":"6","۷":"7","۸":"8","۹":"9"};
  function latinizeDigits(root=document){qsa(".md-typeset :not(code):not(pre):not(kbd):not(samp)").forEach(el=>{
    el.childNodes.forEach(n=>{if(n.nodeType===3&&/[۰-۹]/.test(n.nodeValue)){n.nodeValue=n.nodeValue.replace(/[۰-۹]/g,d=>DIGIT_MAP[d]||d);}});});}
  function enforceRTL(){document.documentElement.setAttribute("dir","rtl");document.documentElement.setAttribute("lang","fa");
    if(document.body)document.body.setAttribute("dir","rtl");}
  function headerNavSearch(){
    const map=new Map([["Home","خانه"],["Getting started","بلوحساب"],["Setup","دیتابیس"],["Plugins","مدیریت ارتباط"],["Reference","منابع انسانی"],["Insiders","بلو وایر"],["Community","بلو ای‌پی‌آی"],["Blog","بلو‌داک"]]);
    const anchors=[...document.querySelectorAll(".md-tabs__link"),...document.querySelectorAll(".md-tabs__item a"),
                   ...document.querySelectorAll("header nav a"),...document.querySelectorAll(".md-header__link"),...document.querySelectorAll(".md-nav__link")];
    anchors.forEach(a=>{const t=(a.textContent||"").replace(/\s+/g," ").trim();if(map.has(t))a.textContent=map.get(t);a.setAttribute("dir","rtl");a.setAttribute("lang","fa");});
    const input=document.querySelector('input[type="text"][data-md-component="search-query"]')||document.querySelector(".md-search__input input")||document.querySelector(".md-search__input");
    if(input)input.setAttribute("placeholder","جست‌وجو…");
    document.querySelectorAll('[data-md-component="source"], .md-source, .md-header__source, .md-header-nav__source').forEach(el=>el.remove());
    document.querySelectorAll('.md-header a').forEach(a=>{if((a.getAttribute('href')||"").includes("github.com/"))a.remove();});
    const brand=document.querySelector(".md-header__topic .md-ellipsis")||document.querySelector(".md-header__title .md-ellipsis"); if(brand)brand.textContent="BlueAPi";
  }
  function hero(){const h=qs(".mdx-hero");if(!h)return;const ti=qs(".mdx-hero__title, .mdx-hero h1",h), le=qs(".mdx-hero__content p, .mdx-hero p",h), btn=qsa(".mdx-hero__content .md-button, .mdx-hero .md-button",h);
    if(ti)ti.textContent="با BlueAPi سریع‌تر مدیریت کنید، کمتر خطا کنید";
    if(le)le.textContent="BlueAPi بازطراحی‌شده با کمک AI: ماژول‌های آماده، گردش‌کارهای هوشمند، جست‌وجوی فارسی، و استقرار روی سرور شما یا ابر. مناسب شرکت‌های در حال رشد و Enterprise.";
    if(btn[0])btn[0].textContent="شروع کنید"; if(btn[1])btn[1].textContent="بیشتر بدانید"; qsa(".mdx-hero *",h).forEach(el=>el.setAttribute("dir","rtl"));}
  function translateExpectHeading(){let h=document.querySelector('#everything-you-would-expect, [id*="everything-you-would-expect"]'); if(h)h=h.closest('h1, h2, h3')||h;
    if(!h){for(const el of document.querySelectorAll('h1, h2, h3')){const t=(el.textContent||'').trim().replace(/\s+/g,' '); if(/^Everything you would expect/i.test(t)){h=el;break;}}}
    if(!h)return; const a=h.querySelector('a, .mdx-anchor, .headerlink'); if(a)a.remove(); h.textContent='همان چیزی که انتظار دارید'; if(a)h.appendChild(a); h.setAttribute('dir','rtl'); h.setAttribute('lang','fa');}
  function sectionExpect(){const wrap=document.querySelector('.mdx-expect')||document.querySelector('section[id*="expect"]')||document.querySelector('[data-section="expect"]'); if(!wrap)return;
    const hd=wrap.querySelector('h1, h2'); if(hd){hd.textContent='همان چیزی که انتظار دارید'; hd.setAttribute('dir','rtl'); hd.setAttribute('lang','fa');}
    const data=[['پنل مدیریت پیشرفتهٔ ناوگان حمل‌ونقل','رهگیری لحظه‌ای GPS، سوابق سرویس و تعمیرات، مصرف سوخت به تفکیک خودرو/راننده، زمان‌بندی بارگیری/تخلیه و محاسبهٔ هزینهٔ سفر.','/blueapi/fleet-management/'],
                ['پنل مدیریت اجاره‌داری و املاک','ثبت ملک و واحدها، قراردادهای اجاره با زمان‌بندی پرداخت/تمدید، یادآوری هوشمند موعدها، نگهداری و تعمیرات دوره‌ای.','/blueapi/lease-management/'],
                ['پنل خدمات پس از فروش پیشرفته','تیکتینگ حرفه‌ای با SLA، چرخهٔ کامل تعمیر (پذیرش تا تحویل)، مدیریت قطعات مصرفی، ارزیابی رضایت مشتری.','/blueapi/after-sales/'],
                ['پنل صدور مجوز و انطباق','فرایندهای چندمرحله‌ای اخذ مجوز، پیگیری وضعیت، تاریخ انقضا و هشدار خودکار، آرشیو مدارک قانونی.','/blueapi/permit-compliance/'],
                ['پنل مدیریت آزمایشگاه (LIMS)','ثبت نمونه و نتایج، مدیریت دستگاه و کالیبراسیون، پیگیری مواد مصرفی، و گزارش‌های استاندارد.','/blueapi/lims/'],
                ['پنل حسابداری بومی','کدینگ استاندارد داخلی، گزارش‌های فصلی، داشبوردهای مدیریتی بومی، بهای تمام‌شده به روش‌های تخصصی.','/blueapi/accounting-local/']];
    const items=Array.from(wrap.querySelectorAll('.mdx-expect__item, .mdx-expect li, .mdx-expect article, li.mdx-expect__item')).filter(el=>el.querySelector('h2, h3'));
    if(items.length){items.slice(0,data.length).forEach((it,i)=>{const [t,d,h]=data[i];const he=it.querySelector('h2, h3'); if(he)he.textContent=t; let p=Array.from(it.querySelectorAll('p')).find(x=>!x.querySelector('a'))||it.querySelector('p'); if(p)p.textContent=d;
      const b=it.querySelector('a.md-button, a[href]'); if(b){b.textContent='مشاهده جزئیات'; if(h)b.setAttribute('href',h);} it.hidden=false; it.querySelectorAll('*').forEach(el=>el.setAttribute('dir','rtl'));});}
    wrap.querySelectorAll('[hidden]').forEach(el=>el.hidden=false); wrap.querySelectorAll('*').forEach(el=>el.setAttribute('dir','rtl'));}
  function translateSpotlightHeading(){let h=document.querySelector('#more-than-just-a-static-site, [id*="more-than-just-a-static-site"]'); if(h)h=h.closest('h1, h2, h3')||h;
    if(!h){for(const el of document.querySelectorAll('h1, h2, h3')){const t=(el.textContent||'').trim().replace(/\s+/g,' '); if(/^More than just a static site/i.test(t)){h=el;break;}}}
    if(!h)return; const a=h.querySelector('a, .mdx-anchor, .headerlink'); if(a)a.remove(); h.textContent='ماژول‌های اصلی'; if(a)h.appendChild(a); h.setAttribute('dir','rtl'); h.setAttribute('lang','fa');}
  function sectionCoreModules(){const sp=qs(".mdx-spotlight"); if(!sp)return; const h=qs("h2, h1",sp), sub=qs("p",sp); if(h)h.textContent="ماژول‌های اصلی"; if(sub)sub.textContent="پایه‌های قدرتمند و کاملاً قابل‌سفارشی‌سازی برای شرکت شما";
    const figs=qsa(".mdx-spotlight__feature",sp), data=[["حسابداری","مدیریت حساب‌ها، تراکنش‌ها و مالیات‌ها به‌سادگی.","/blueapi/modules/accounting/"],["منابع انسانی (BlueHab)","حضور و غیاب، مرخصی، هزینه‌ها، حقوق و دستمزد، جذب و ارزیابی.","/bluehab/"],["مدیریت ارتباط با مشتری (CRM)","از سرنخ تا فرصت، ایمیل و تماس – کل چرخه فروش در یک‌جا.","/blueapi/modules/crm/"],["تولید","برنامه‌ریزی ظرفیت، گردش تولید، مصرف مواد، برون‌سپاری و بیشتر.","/blueapi/modules/manufacturing/"],["مدیریت سفارش","رهگیری هوشمند انجام سفارش، کنترل موجودی، پروموشن و توزیع.","/blueapi/modules/order-management/"],["مدیریت دارایی","ثبت، استهلاک و سرمایه‌گذاری/خروج دارایی‌ها – همه در یک پنل.","/blueapi/modules/asset-management/"]];
    for(let i=0;i<Math.min(figs.length,data.length);i++){const cap=qs("figcaption",figs[i])||figs[i]; cap.innerHTML=`<h2>${data[i][0]}</h2><p>${data[i][1]}</p><p><a class="md-button" href="${data[i][2]}">بیشتر بدانید →</a></p>`;}
    qsa("[hidden]",sp).forEach(el=>el.hidden=false); qsa(".mdx-spotlight *",sp).forEach(el=>el.setAttribute("dir","rtl"));}
  function sectionDevDocsPlain(){const kill=node=>{const raw=(node?.innerText||node?.textContent||"");const t=raw.normalize("NFKC").replace(/\s+/g," ").trim().toLowerCase();return t.includes("trusted")&&t.includes("industry");};
    document.querySelectorAll("h1, h2, h3").forEach(h=>{if(kill(h))h.remove();});
    const sec=document.querySelector(".mdx-partners")||document.querySelector(".mdx-trust"); if(!sec)return;
    if(sec.previousElementSibling&&kill(sec.previousElementSibling))sec.previousElementSibling.remove();
    if(sec.nextElementSibling&&kill(sec.nextElementSibling))sec.nextElementSibling.remove();
    sec.querySelectorAll(":scope > h1, :scope > h2, :scope > h3, :scope > header, :scope > .mdx-spotlight__title").forEach(el=>el.remove());
    sec.innerHTML=`<div class="md-typeset blue-devdocs">
      <h2 class="blue-devdocs__title">مستندات توسعه‌دهندگان</h2>
      <section class="blue-item"><h3>BlueWire Framework</h3><p>فریم‌ورک BlueWire (Python/JS)، هستهٔ BlueAPi برای ساخت اپ و یکپارچه‌سازی‌ها.</p><p><a class="md-button" href="/bluewire/">بیشتر بدانید →</a></p></section>
      <section class="blue-item"><h3>آموزش قدم‌به‌قدم</h3><p>مسیر ساخت اپ/افزونهٔ سفارشی با مثال‌های عملی و معماری فریم‌ورک.</p><p><a class="md-button" href="/bluewire/tutorials/">بیشتر بدانید →</a></p></section>
      <section class="blue-item"><h3>Developer API</h3><p>API برای یکپارچه‌سازی‌ها و افزونه‌ها (REST/GraphQL/Webhooks).</p><p><a class="md-button" href="/bluewire/api/">بیشتر بدانید →</a></p></section>
    </div>`;
    sec.querySelectorAll("*").forEach(el=>{el.setAttribute("dir","rtl");el.setAttribute("lang","fa");});}
  function sectionRefArchitectures(){const host=document.querySelector(".mdx-users")||document.querySelector('[data-section="testimonials"]'); if(!host)return;
    document.querySelectorAll("h1,h2,h3,h4,h5").forEach(h=>{const t=(h.textContent||"").trim().toLowerCase(); if(t.includes("what our users say"))h.remove();});
    host.innerHTML=`<section class="ref-arch" dir="rtl">
      <h2 class="ref-arch__title">معماری‌های مرجع</h2>
      <p class="ref-arch__lead">استقرار <strong>BlueAPi</strong> را با پیکربندی‌های پیشنهادی برای مقیاس‌های مختلف انجام دهید.</p>
      <div class="ref-arch__row ref-arch__row--top" dir="ltr">
        <a class="ref-card" href="/architecture/1k/"><span class="ref-card__num">1,000</span><span class="ref-card__label">users</span><span class="ref-card__chev">→</span></a>
        <a class="ref-card" href="/architecture/2k/"><span class="ref-card__num">2,000</span><span class="ref-card__label">users</span><span class="ref-card__chev">→</span></a>
        <a class="ref-card" href="/architecture/3k/"><span class="ref-card__num">3,000</span><span class="ref-card__label">users</span><span class="ref-card__chev">→</span></a>
        <a class="ref-card" href="/architecture/5k/"><span class="ref-card__num">5,000</span><span class="ref-card__label">users</span><span class="ref-card__chev">→</span></a>
      </div>
      <div class="ref-arch__row ref-arch__row--bottom" dir="ltr">
        <a class="ref-card" href="/architecture/10k/"><span class="ref-card__num">10,000</span><span class="ref-card__label">users</span><span class="ref-card__chev">→</span></a>
        <a class="ref-card" href="/architecture/25k/"><span class="ref-card__num">25,000</span><span class="ref-card__label">users</span><span class="ref-card__chev">→</span></a>
        <a class="ref-card" href="/architecture/50k/"><span class="ref-card__num">50,000</span><span class="ref-card__label">users</span><span class="ref-card__chev">→</span></a>
      </div>
    </section>`;
    host.querySelectorAll(".ref-arch__row, .ref-card, .ref-card *").forEach(el=>el.setAttribute("dir","ltr"));}
  /* فقط در صفحهٔ اصلی اجرا شود */
  const isHome=()=>!!document.querySelector('.mdx-hero, .mdx-spotlight, .mdx-expect, .mdx-partners, .mdx-users');
  function sectionFooter(){
    try{
      document.querySelectorAll('.md-footer-nav, .md-footer__link--next, .md-footer__link--prev').forEach(el=>el.remove());
      let sec=document.querySelector('.mdx-connect'); if(!sec){ if(!isHome()) return; } // فقط هوم
      if(!sec){console.warn("[BlueAPi] footer section not found on home"); return;}
      sec.innerHTML=`<div class="mdx-connect md-typeset" dir="rtl">
        <div class="blue-footer-grid">
          <div class="blue-footer-col">
            <h2>بیایید در تماس باشیم</h2>
            <ul class="mdx-connect__list">
              <li>تلگرام <a href="https://t.me/BlueAPi" target="_blank" rel="noopener">BlueAPi</a></li>
              <li>ایکس (توییتر) <a href="https://twitter.com/BlueAPi" target="_blank" rel="noopener">@BlueAPi</a></li>
              <li>BlueAPi در <a href="https://github.com/BlueAPi" target="_blank" rel="noopener">GitHub</a></li>
              <li>ایماژهای رسمی در <a href="https://hub.docker.com/u/blueapi" target="_blank" rel="noopener">Docker Hub</a></li>
              <li>بسته‌ها در <a href="https://pypi.org" target="_blank" rel="noopener">PyPI</a></li>
            </ul>
          </div>
          <div class="blue-footer-col">
            <h2>حامی BlueAPi شوید</h2>
            <p>با پیوستن به برنامهٔ حمایتی، زودتر از همه به ویژگی‌های تازه دسترسی پیدا می‌کنید و به توسعهٔ <strong>BlueAPi</strong> و فریم‌ورک <strong>BlueWire</strong> کمک می‌کنید.</p>
            <p><a class="md-button" href="/support/" rel="noopener">بیشتر بدانید</a></p>
          </div>
        </div>
      </div>`;
      const meta=document.querySelector('.md-footer-meta .md-footer-meta__inner')||document.querySelector('.md-footer-meta')||document.querySelector('footer.md-footer');
      if(meta&&!meta.querySelector('.blue-copyright')){
        Array.from(meta.querySelectorAll('*')).forEach(el=>{const t=(el.textContent||'').trim(); if(/Material for MkDocs/i.test(t)||/Insiders/i.test(t)||/Martin Donath/i.test(t)){el.style.display='none';}});
        const cp=document.createElement('div'); cp.className='blue-copyright md-typeset'; cp.setAttribute('dir','rtl');
        cp.innerHTML='<div>Copyright © 2018 - 2025&nbsp;<strong>Sarmad Afzali</strong></div><div>Made with <strong>BlueAPi</strong> / <strong>BlueWire</strong></div>'; meta.appendChild(cp);
      }
    }catch(e){console.error("[BlueAPi] footer patch error:",e);}
  }
  function forceLTRCode(){qsa('code, pre, pre code, table code, .md-clipboard, .md-typeset a[href^="http"]').forEach(el=>{el.setAttribute("dir","ltr");});}
  function applyAll(){
    enforceRTL(); headerNavSearch(); forceLTRCode(); latinizeDigits();
    if(isHome()){ hero(); sectionCoreModules(); sectionRefArchitectures(); sectionExpect(); translateSpotlightHeading(); sectionDevDocsPlain(); translateExpectHeading(); sectionFooter(); }
  }
  ready(applyAll);
  if(window.document$&&typeof window.document$.subscribe==="function"){ window.document$.subscribe(()=>{requestAnimationFrame(applyAll);}); }
  else{ const debounced=debounce(applyAll,250); new MutationObserver(debounced).observe(document.documentElement,{childList:true,subtree:true}); }
})();
/* BDM: collapse sidebar by default, open only active trail */
(function(){
  function collapse(){
    document.querySelectorAll('.md-nav__item--nested > input').forEach(cb=>cb.checked=false);
    let act=document.querySelector('.md-nav__link--active');
    while(act){
      const nest=act.closest('.md-nav__item--nested');
      if(!nest) break;
      const cb=nest.querySelector(':scope > input');
      if(cb) cb.checked=true;
      act=nest.parentElement.closest('.md-nav__item')?.querySelector(':scope > .md-nav__link');
    }
  }
  const run=()=>collapse();
  document.addEventListener('DOMContentLoaded',run);
  if(window.document$ && window.document$.subscribe) window.document$.subscribe(run);
})();
/* BDM: rename & re-link top tabs on homepage and docs */
(function(){
  const map=[
    ['Home','خانه','/'],
    ['Getting started','بلوحساب','/blueapi/bluehesab/'],
    ['Setup','دیتابیس','/blueapi/database/'],
    ['Plugins','مدیریت ارتباط','/blueapi/crm/'],
    ['Reference','منابع انسانی','/blueapi/hr/'],
    ['Insiders','بلو وایر','/blueapi/bluewire/'],
    ['Community','بلو ای‌پی‌آی','/blueapi/blueapi/'],
    ['Blog','بلو‌داک','/blueapi/bluedoc/'],
  ];
  function retitle(){
    document.querySelectorAll('header a, .md-tabs__item a, .md-tabs__link').forEach(a=>{
      const t=(a.textContent||'').trim();
      const m=map.find(x=>x[0]===t);
      if(m){ a.textContent=m[1]; if(m[2]) a.setAttribute('href', m[2]); }
    });
  }
  const run=()=>retitle();
  document.addEventListener('DOMContentLoaded',run);
  if(window.document$ && window.document$.subscribe) window.document$.subscribe(run);
})();
(function(){
  const map=[['Home','خانه'],['Getting started','بلوحساب'],['Setup','دیتابیس'],['Plugins','مدیریت ارتباط'],['Reference','منابع انسانی'],['Insiders','بلو وایر'],['Community','بلو ای‌پی‌آی'],['Blog','بلو‌داک']];
  function retitle(){
    document.querySelectorAll('.md-tabs__link .md-ellipsis, .md-tabs__link, header nav a').forEach(el=>{
      const t=(el.textContent||'').trim();
      const m=map.find(x=>x[0]===t);
      if(m){ el.textContent=m[1]; }
    });
  }
  document.addEventListener('DOMContentLoaded',retitle);
  if(window.document$ && window.document$.subscribe) window.document$.subscribe(retitle);
})();
/* BDM: hard-collapse + open active trail (works on SPA and DOM changes) */
(function(){
  function apply(){
    const root=document.querySelector('.md-sidebar--primary'); if(!root) return;

    // 1) بستن همه
    root.querySelectorAll('.md-nav__item--nested > input.md-nav__toggle').forEach(i=>{ i.checked=false; });

    // 2) یافتن لینک فعال
    let active = root.querySelector('.md-nav__link--active,[aria-current="page"],[aria-current="true"]');
    if(!active){
      //fallback: اگر فقط هایلایت روی آیتم والد است
      active = root.querySelector('.md-nav__item--active > .md-nav__link');
    }
    if(!active) return;

    // 3) باز کردن همهٔ والدهای فعال
    let it = active.closest('.md-nav__item');
    while(it){
      const tgl = it.querySelector(':scope > input.md-nav__toggle');
      if(tgl) tgl.checked = true;
      it = it.parentElement ? it.parentElement.closest('.md-nav__item') : null;
    }
  }

  const run = ()=> setTimeout(apply, 60);
  document.addEventListener('DOMContentLoaded', run);
  if(window.document$ && window.document$.subscribe) window.document$.subscribe(run);

  // واکنش به تغییرات DOM (مثلاً بارگذاری بخش‌ها)
  new MutationObserver(run).observe(document.documentElement,{childList:true,subtree:true});
})();
