(function(){
if (!/^\/app(\/|$)/.test(location.pathname)) return;
const DOCS = "https://docs.bluehesab.ir/";
const SUPPORT = "https://docs.bluehesab.ir/";
const norm = s => String(s||"").replace(/\s+/g," ").replace(/[\u200c\u200f\u202a-\u202e]/g,"").trim();


function ensureShortcuts(menu){
if ([...menu.querySelectorAll('a')].some(a=>/میانبرهای صفحه‌کلید|Keyboard Shortcuts/i.test(norm(a.textContent)))) return;
const li=document.createElement('li'); const a=document.createElement('a');
a.className='dropdown-item'; a.textContent='میانبرهای صفحه‌کلید'; a.href='#';
a.addEventListener('click', (e)=>{
e.preventDefault();
try { if (frappe?.ui?.keys?.show_shortcuts) return frappe.ui.keys.show_shortcuts(); } catch(_){ }
document.dispatchEvent(new KeyboardEvent('keydown',{key:'?',code:'Slash',shiftKey:true,which:191,keyCode:191,bubbles:true}));
});
li.appendChild(a); menu.appendChild(li);
}


function rebuild(){
const help=document.querySelector('.dropdown-help');
const menu=help && help.querySelector('.dropdown-menu');
if(!menu) return;
menu.innerHTML='';
const mk=(txt,href)=>{ const li=document.createElement('li'),a=document.createElement('a'); a.className='dropdown-item'; a.textContent=txt; a.href=href; a.target='_blank'; a.rel='noopener'; li.appendChild(a); return li; };
menu.appendChild(mk('مستندات', DOCS));
menu.appendChild(mk('پشتیبانی BlueAPI', SUPPORT));
ensureShortcuts(menu);
}


document.addEventListener('shown.bs.dropdown', e=>{ if(e.target?.classList?.contains('dropdown-help')) setTimeout(rebuild,0); }, true);
let n=0; const id=setInterval(()=>{ rebuild(); if(++n>8) clearInterval(id); }, 500);


// Fallback: override toolbar provider if menu اصلاً ساخته نشود
function patchToolbar(){
try{
if (frappe?.ui?.toolbar && typeof frappe.ui.toolbar.get_help_menu_items === 'function'){
frappe.ui.toolbar.get_help_menu_items = function(){
return [
{ label:'مستندات', action:()=>open(DOCS,'_blank','noopener') },
{ label:'پشتیبانی BlueAPI', action:()=>open(SUPPORT,'_blank','noopener') },
{ label:'میانبرهای صفحه‌کلید', action:()=>{
try{ if (frappe?.ui?.keys?.show_shortcuts) return frappe.ui.keys.show_shortcuts(); }catch(_){}
document.dispatchEvent(new KeyboardEvent('keydown',{key:'?',code:'Slash',shiftKey:true,which:191,keyCode:191,bubbles:true}));
}
}
];
};
}
}catch(_){ }
}
if (document.readyState!=='loading') patchToolbar(); else document.addEventListener('DOMContentLoaded', patchToolbar);
if (window.frappe && frappe.after_ajax) frappe.after_ajax(()=>setTimeout(patchToolbar,0));


// Link guard برای هر لینک قدیمی
document.addEventListener('click', e=>{
const a=e.target.closest('a[href]'); if(!a) return;
if (/support\.frappe\.io\/help/i.test(a.href)) { e.preventDefault(); open(SUPPORT,'_blank','noopener'); }
if (/docs\.(erpnext|erp)\.com/i.test(a.href)) { e.preventDefault(); open(DOCS,'_blank','noopener'); }
}, true);
})();