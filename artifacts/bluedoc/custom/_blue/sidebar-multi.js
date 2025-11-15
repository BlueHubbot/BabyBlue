(function(){
  const Q='.md-sidebar--primary input.md-nav__toggle';

  function openActive(){
    const root=document.querySelector('.md-sidebar--primary'); if(!root) return;
    let active=root.querySelector('.md-nav__link--active,[aria-current="page"],[aria-current="true"]')
             || root.querySelector('.md-nav__item--active > .md-nav__link');
    if(!active) return;
    let it=active.closest('.md-nav__item');
    while(it){
      const t=it.querySelector(':scope > input.md-nav__toggle'); if(t) t.checked=true;
      it=it.parentElement?it.parentElement.closest('.md-nav__item'):null;
    }
  }

  function initOnce(){
    if(window.__bdmSidebarInit) return; window.__bdmSidebarInit=true;
    // بارِ اول: همه بسته + زنجیرهٔ فعال باز شود (بعد از این، به حالت‌ها دست نمی‌زنیم)
    document.querySelectorAll(Q).forEach(i=>i.checked=false);
    openActive();

    // اجازهٔ چندتایی باز/بسته: هیچ بستن اجباری انجام نده
    document.querySelectorAll(Q).forEach(i=>{
      if(i.dataset.bdmWired) return; i.dataset.bdmWired='1';
      i.addEventListener('change',()=>{/* no-op: keep others as-is */});
    });
  }

  document.addEventListener('DOMContentLoaded', initOnce);
  if(window.document$ && document$.subscribe) document$.subscribe(()=>setTimeout(openActive,50));
})();
