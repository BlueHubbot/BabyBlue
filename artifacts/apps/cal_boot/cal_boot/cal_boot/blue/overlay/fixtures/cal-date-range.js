// == CAL :: DATE-RANGE-PATCH v1 (global) ==
(function(){
  if (window.__calDRPPatched) return; window.__calDRPPatched = true;

  function MODE(){ try{ return localStorage.getItem('CAL_MODE') || 'jalali'; }catch(e){ return 'jalali'; } }

  async function ensureLibs(){
    function addCss(h){ return new Promise(function(r,j){ try{
      if(document.querySelector("link[href^='"+h+"']")) return r();
      var l=document.createElement('link'); l.rel='stylesheet'; l.href=h;
      l.onload=r; l.onerror=j; document.head.appendChild(l);
    }catch(e){ j(e); } }); }
    function addJs(s){ return new Promise(function(r,j){ try{
      if(document.querySelector("script[src^='"+s+"']")) return r();
      var e=document.createElement('script'); e.src=s;
      e.onload=r; e.onerror=j; document.body.appendChild(e);
    }catch(e){ j(e); } }); }
    await addCss('https://cdn.jsdelivr.net/npm/persian-datepicker@1.2.0/dist/css/persian-datepicker.min.css');
    await addJs ('https://cdn.jsdelivr.net/npm/persian-date@1.1.0/dist/persian-date.min.js');
    await addJs ('https://cdn.jsdelivr.net/npm/persian-datepicker@1.2.0/dist/js/persian-datepicker.min.js');
    return !!(window.persianDate && window.jQuery && jQuery.fn.pDatepicker);
  }

  function bindPair(inpFa, inpFa2, inpEn, inpEn2){
    try{ jQuery(inpFa).pDatepicker('destroy'); jQuery(inpFa2).pDatepicker('destroy'); }catch(e){}
    jQuery(inpFa).pDatepicker({
      autoClose:true, initialValue:false, format:'YYYY/MM/DD',
      altField:inpEn, altFormat:'YYYY-MM-DD',
      onSelect:function(unix){ try{ var d=new persianDate(unix).toDate(); jQuery(inpFa2).pDatepicker('setMinDate', d.getTime()); }catch(e){} }
    });
    jQuery(inpFa2).pDatepicker({
      autoClose:true, initialValue:false, format:'YYYY/MM/DD',
      altField:inpEn2, altFormat:'YYYY-MM-DD',
      onSelect:function(unix){ try{ var d=new persianDate(unix).toDate(); jQuery(inpFa).pDatepicker('setMaxDate', d.getTime()); }catch(e){} }
    });
  }

  (function install(){
    if (!window.frappe || !frappe.ui) return;
    var Orig = frappe.ui.DateRangePicker;
    if (!Orig || frappe.__CAL_Orig_DRP) return;
    frappe.__CAL_Orig_DRP = Orig;

    frappe.ui.DateRangePicker = function(opts){
      this.opts = opts || {};
      this.from_date = this.opts.from_date || null;
      this.to_date   = this.opts.to_date   || null;

      var self = this;
      this.show = async function(){
        if (MODE() !== 'jalali' || !(await ensureLibs())) { try{ return new Orig(self.opts).show(); }catch(e){ return; } }
        var dlg = new frappe.ui.Dialog({
          title: 'انتخاب بازهٔ زمانی (شمسی)',
          fields: [
            {fieldtype:'Section Break'},
            {label:'از', fieldname:'from_fa', fieldtype:'Data'},
            {fieldtype:'Column Break'},
            {label:'تا', fieldname:'to_fa', fieldtype:'Data'},
            {fieldtype:'Section Break'},
            {fieldtype:'HTML', fieldname:'hint', options:'<div style="opacity:.7;font-size:12px">نمایش شمسی؛ ارسال به سرور: <code>YYYY-MM-DD</code> (میلادی)</div>'}
          ],
          primary_action_label: 'اعمال',
          primary_action: function(){
            var from_g = dlg._from_en.value || '';
            var to_g   = dlg._to_en.value   || '';
            try{
              if (typeof self.opts.set_value === 'function') self.opts.set_value(from_g, to_g);
              if (typeof self.opts.on_change === 'function') self.opts.on_change(from_g, to_g);
              if (typeof self.opts.callback === 'function') self.opts.callback(from_g, to_g);
              if (typeof self.opts.update_date_range === 'function') self.opts.update_date_range(from_g, to_g);
            }catch(e){}
            dlg.hide();
          }
        });
        dlg._from_en = document.createElement('input');
        dlg._to_en   = document.createElement('input');
        dlg._from_en.type='hidden'; dlg._to_en.type='hidden';
        dlg.body.appendChild(dlg._from_en); dlg.body.appendChild(dlg._to_en);

        var fromFa = dlg.get_field('from_fa').$input[0];
        var toFa   = dlg.get_field('to_fa').$input[0];
        try{ fromFa.classList.add('form-control'); toFa.classList.add('form-control'); }catch(e){}
        bindPair(fromFa, toFa, dlg._from_en, dlg._to_en);
        dlg.show();
      };

      this.hide = function(){};
      return this;
    };
  })();
})();
