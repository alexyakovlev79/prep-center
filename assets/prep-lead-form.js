/* Prep-Center: one form implementation for inline blocks and modal windows. */
(function(){
'use strict';
if(window.__PREP_CENTER_LEAD_FORM_ACTIVE__)return;
window.__PREP_CENTER_LEAD_FORM_ACTIVE__=true;
const ENDPOINT=String(window.PREP_CENTER_FORM_ENDPOINT||'').trim();
const COUNTRIES=[{"name":"Afghanistan (افغانستان‎)","mask":"+93-99-999-9999","iso2":"af","dial":"+93"},{"name":"Albania (Shqipëri)","mask":"+355(999) 999-999","iso2":"al","dial":"+355"},{"name":"Algeria (الجزائر‎)","mask":"+213-99-999-9999","iso2":"dz","dial":"+213"},{"name":"Andorra","mask":"+376-999-999","iso2":"ad","dial":"+376"},{"name":"Angola","mask":"+244(999) 999-999","iso2":"ao","dial":"+244"},{"name":"Armenia (Հայաստան)","mask":"+374-99-999-999","iso2":"am","dial":"+374"},{"name":"Antigua and Barbuda","mask":"+1 (268)999-9999","iso2":"ag","dial":"+1 (268)"},{"name":"Argentina","mask":"+54(999) 9999-9999","iso2":"ar","dial":"+54"},{"name":"Australia","mask":"+61-99-9999-9999","iso2":"au","dial":"+61"},{"name":"Austria (Österreich)","mask":"+43(999) 999-99999","iso2":"at","dial":"+43"},{"name":"Azerbaijan (Azərbaycan)","mask":"+994-99-999-99-99","iso2":"az","dial":"+994"},{"name":"Bahamas","mask":"+1 (242)999-9999","iso2":"bs","dial":"+1 (242)"},{"name":"Bahrain (البحرين‎)","mask":"+973-9999-9999","iso2":"bh","dial":"+973"},{"name":"Bangladesh (বাংলাদেশ)","mask":"+880-9999-999999","iso2":"bd","dial":"+880"},{"name":"Barbados","mask":"+1 (246)999-9999","iso2":"bb","dial":"+1 (246)"},{"name":"Belarus (Беларусь)","mask":"+375(99) 999-99-99","iso2":"by","dial":"+375"},{"name":"Belgium (België)","mask":"+32(999) 999-999","iso2":"be","dial":"+32"},{"name":"Belize","mask":"+501-999-9999","iso2":"bz","dial":"+501"},{"name":"Benin (Bénin)","mask":"+229-99-99-9999","iso2":"bj","dial":"+229"},{"name":"Bhutan (འབྲུག)","mask":"+975-9-999-9999","iso2":"bt","dial":"+975"},{"name":"Bolivia","mask":"+591-9-999-9999","iso2":"bo","dial":"+591"},{"name":"Bosnia and Herzegovina","mask":"+387-99-999-999","iso2":"ba","dial":"+387"},{"name":"Botswana","mask":"+267-99-999-999","iso2":"bw","dial":"+267"},{"name":"Brazil (Brasil)","mask":"+55(99) 99999-9999","iso2":"br","dial":"+55"},{"name":"Brunei","mask":"+673-999-9999","iso2":"bn","dial":"+673"},{"name":"Bulgaria (България)","mask":"+359(999) 999-999","iso2":"bg","dial":"+359"},{"name":"Burkina Faso","mask":"+226-99-99-9999","iso2":"bf","dial":"+226"},{"name":"Burundi (Uburundi)","mask":"+257-99-99-9999","iso2":"bi","dial":"+257"},{"name":"Cambodia (កម្ពុជា)","mask":"+855-99-999-999","iso2":"kh","dial":"+855"},{"name":"Cameroon (Cameroun)","mask":"+237-9-99-99-99-99","iso2":"cm","dial":"+237"},{"name":"Canada","mask":"+1(999) 999-9999","iso2":"ca","dial":"+1"},{"name":"Cape Verde (Kabu Verdi)","mask":"+238(999) 99-99","iso2":"cv","dial":"+238"},{"name":"Central African Republic (République centrafricaine)","mask":"+236-99-99-9999","iso2":"cf","dial":"+236"},{"name":"Chad (Tchad)","mask":"+235-99-99-99-99","iso2":"td","dial":"+235"},{"name":"Chile","mask":"+56-9-9999-9999","iso2":"cl","dial":"+56"},{"name":"China (中国)","mask":"+86(999) 9999-9999","iso2":"cn","dial":"+86"},{"name":"Colombia","mask":"+57(999) 999-9999","iso2":"co","dial":"+57"},{"name":"Comoros (جزر القمر‎)","mask":"+269-99-99999","iso2":"km","dial":"+269"},{"name":"Congo (DRC) (Jamhuri ya Kidemokrasia ya Kongo)","mask":"+243(999) 999-999","iso2":"cd","dial":"+243"},{"name":"Congo (Republic) (Congo-Brazzaville)","mask":"+242-99-999-9999","iso2":"cg","dial":"+242"},{"name":"Cook Islands","mask":"+682-99-999","iso2":"ck","dial":"+682"},{"name":"Costa Rica","mask":"+506-9999-9999","iso2":"cr","dial":"+506"},{"name":"Cote d’Ivoire","mask":"+225-99-999-999","iso2":"ci","dial":"+225"},{"name":"Croatia (Hrvatska)","mask":"+385-99-999-9999","iso2":"hr","dial":"+385"},{"name":"Cuba","mask":"+53-9-999-9999","iso2":"cu","dial":"+53"},{"name":"Cyprus (Κύπρος)","mask":"+357-99-999-999","iso2":"cy","dial":"+357"},{"name":"Czech Republic (Česká republika)","mask":"+420(999) 999-999","iso2":"cz","dial":"+420"},{"name":"Denmark (Danmark)","mask":"+45-99-99-99-99","iso2":"dk","dial":"+45"},{"name":"Djibouti","mask":"+253-99-99-99-99","iso2":"dj","dial":"+253"},{"name":"Dominica","mask":"+1 (767)999-9999","iso2":"dm","dial":"+1 (767)"},{"name":"Dominican Republic (República Dominicana)","mask":"+1(999) 999-9999","iso2":"do","dial":"+1"},{"name":"Ecuador","mask":"+593-9-999-9999","iso2":"ec","dial":"+593"},{"name":"Egypt (مصر‎)","mask":"+20(999) 999-9999","iso2":"eg","dial":"+20"},{"name":"El Salvador","mask":"+503-99-99-9999","iso2":"sv","dial":"+503"},{"name":"Equatorial Guinea (Guinea Ecuatorial)","mask":"+240-99-999-9999","iso2":"gq","dial":"+240"},{"name":"Eritrea","mask":"+291-9-999-999","iso2":"er","dial":"+291"},{"name":"Estonia (Eesti)","mask":"+372-9999-9999","iso2":"ee","dial":"+372"},{"name":"Ethiopia","mask":"+251-99-999-9999","iso2":"et","dial":"+251"},{"name":"Fiji","mask":"+679-999-9999","iso2":"fj","dial":"+679"},{"name":"Finland (Suomi)","mask":"+358-999-9999999","iso2":"fi","dial":"+358"},{"name":"France","mask":"+33(999) 999-999","iso2":"fr","dial":"+33"},{"name":"Gabon","mask":"+241-9-99-99-99","iso2":"ga","dial":"+241"},{"name":"Gambia","mask":"+220(999) 99-99","iso2":"gm","dial":"+220"},{"name":"Georgia (საქართველო)","mask":"+995(999) 999-999","iso2":"ge","dial":"+995"},{"name":"Germany (Deutschland)","mask":"+49(999) 999-99999","iso2":"de","dial":"+49"},{"name":"Ghana (Gaana)","mask":"+233(999) 999-999","iso2":"gh","dial":"+233"},{"name":"Greece (Ελλάδα)","mask":"+30(999) 999-9999","iso2":"gr","dial":"+30"},{"name":"Grenada","mask":"+1 (473)999-9999","iso2":"gd","dial":"+1 (473)"},{"name":"Guatemala","mask":"+502-9-999-9999","iso2":"gt","dial":"+502"},{"name":"Guinea (Guinée)","mask":"+224-999-99-99-99","iso2":"gn","dial":"+224"},{"name":"Guinea-Bissau (Guiné Bissau)","mask":"+245-9-999999","iso2":"gw","dial":"+245"},{"name":"Guyana","mask":"+592-999-9999","iso2":"gy","dial":"+592"},{"name":"Haiti","mask":"+509-99-99-9999","iso2":"ht","dial":"+509"},{"name":"Honduras","mask":"+504-9999-9999","iso2":"hn","dial":"+504"},{"name":"Hong Kong (香港)","mask":"+852-9999-9999","iso2":"hk","dial":"+852"},{"name":"Hungary (Magyarország)","mask":"+36(999) 999-999","iso2":"hu","dial":"+36"},{"name":"Iceland (Ísland)","mask":"+354-999-9999","iso2":"is","dial":"+354"},{"name":"India (भारत)","mask":"+91(9999) 999-999","iso2":"in","dial":"+91"},{"name":"Indonesia","mask":"+62(999) 999-99-999","iso2":"id","dial":"+62"},{"name":"Iran (ایران‎)","mask":"+98(999) 999-9999","iso2":"ir","dial":"+98"},{"name":"Iraq (العراق‎)","mask":"+964(999) 999-9999","iso2":"iq","dial":"+964"},{"name":"Ireland","mask":"+353(999) 999-999","iso2":"ie","dial":"+353"},{"name":"Israel (ישראל‎)","mask":"+972-999-999-9999","iso2":"il","dial":"+972"},{"name":"Italy (Italia)","mask":"+39(999) 9999-999","iso2":"it","dial":"+39"},{"name":"Jamaica","mask":"+1(999) 999-9999","iso2":"jm","dial":"+1"},{"name":"Japan (日本)","mask":"+81-99-9999-9999","iso2":"jp","dial":"+81"},{"name":"Jordan (الأردن‎)","mask":"+962-9-9999-9999","iso2":"jo","dial":"+962"},{"name":"Kazakhstan (Казахстан)","mask":"+7(999) 999-99-99","iso2":"kz","dial":"+7"},{"name":"Kenya","mask":"+254-999-999999","iso2":"ke","dial":"+254"},{"name":"Kiribati","mask":"+686-99-999","iso2":"ki","dial":"+686"},{"name":"Kuwait (الكويت‎)","mask":"+965-9999-9999","iso2":"kw","dial":"+965"},{"name":"Kyrgyzstan (Кыргызстан)","mask":"+996(999) 999-999","iso2":"kg","dial":"+996"},{"name":"Laos (ລາວ)","mask":"+856-99-999-999","iso2":"la","dial":"+856"},{"name":"Latvia (Latvija)","mask":"+371-99-999-999","iso2":"lv","dial":"+371"},{"name":"Lebanon (لبنان‎)","mask":"+961-99-999-999","iso2":"lb","dial":"+961"},{"name":"Lesotho","mask":"+266-9-999-9999","iso2":"ls","dial":"+266"},{"name":"Liberia","mask":"+231-99-999-9999","iso2":"lr","dial":"+231"},{"name":"Libya (ليبيا‎)","mask":"+218-99-999-999","iso2":"ly","dial":"+218"},{"name":"Liechtenstein","mask":"+423-999-99-99","iso2":"li","dial":"+423"},{"name":"Lithuania (Lietuva)","mask":"+370(999) 99-999","iso2":"lt","dial":"+370"},{"name":"Luxembourg","mask":"+352(999) 999-999","iso2":"lu","dial":"+352"},{"name":"Macao","mask":"+853-9999-9999","iso2":"mo","dial":"+853"},{"name":"Macedonia (FYROM) (Македонија)","mask":"+389-99-999-999","iso2":"mk","dial":"+389"},{"name":"Madagascar (Madagasikara)","mask":"+261-99-99-99999","iso2":"mg","dial":"+261"},{"name":"Malawi","mask":"+265-9-9999-9999","iso2":"mw","dial":"+265"},{"name":"Malaysia","mask":"+60-99-999-9999","iso2":"my","dial":"+60"},{"name":"Maldives","mask":"+960-999-9999","iso2":"mv","dial":"+960"},{"name":"Mali","mask":"+223-99-99-9999","iso2":"ml","dial":"+223"},{"name":"Malta","mask":"+356-9999-9999","iso2":"mt","dial":"+356"},{"name":"Marshall Islands","mask":"+692-999-9999","iso2":"mh","dial":"+692"},{"name":"Mauritania (موريتانيا‎)","mask":"+222-99-99-9999","iso2":"mr","dial":"+222"},{"name":"Mauritius (Moris)","mask":"+230-999-9999","iso2":"mu","dial":"+230"},{"name":"Mexico (México)","mask":"+52(999) 999-9999","iso2":"mx","dial":"+52"},{"name":"Micronesia","mask":"+691-999-9999","iso2":"fm","dial":"+691"},{"name":"Moldova (Republica Moldova)","mask":"+373-9999-9999","iso2":"md","dial":"+373"},{"name":"Monaco","mask":"+377-99-999-999","iso2":"mc","dial":"+377"},{"name":"Mongolia (Монгол)","mask":"+976-99-99-9999","iso2":"mn","dial":"+976"},{"name":"Montenegro (Crna Gora)","mask":"+382-99-999-999","iso2":"me","dial":"+382"},{"name":"Morocco (المغرب‎)","mask":"+212-99-9999-999","iso2":"ma","dial":"+212"},{"name":"Mozambique (Moçambique)","mask":"+258-99-999-999","iso2":"mz","dial":"+258"},{"name":"Myanmar (Burma) (မြန်မာ)","mask":"+95-99-999-999","iso2":"mm","dial":"+95"},{"name":"Namibia (Namibië)","mask":"+264-99-999-9999","iso2":"na","dial":"+264"},{"name":"Nauru","mask":"+674-999-9999","iso2":"nr","dial":"+674"},{"name":"Nepal (नेपाल)","mask":"+977-99-999-999","iso2":"np","dial":"+977"},{"name":"Netherlands (Nederland)","mask":"+31-99-999-9999","iso2":"nl","dial":"+31"},{"name":"New Zealand","mask":"+64(999) 999-999","iso2":"nz","dial":"+64"},{"name":"Nicaragua","mask":"+505-9999-9999","iso2":"ni","dial":"+505"},{"name":"Niger (Nijar)","mask":"+227-99-99-9999","iso2":"ne","dial":"+227"},{"name":"Nigeria","mask":"+234-999-999-9999","iso2":"ng","dial":"+234"},{"name":"Niue","mask":"+683-9999","iso2":"nu","dial":"+683"},{"name":"North Korea (조선 민주주의 인민 공화국)","mask":"+850-99-999-999","iso2":"kp","dial":"+850"},{"name":"Norway (Norge)","mask":"+47(999) 99-999","iso2":"no","dial":"+47"},{"name":"Oman (عُمان‎)","mask":"+968-99-999-999","iso2":"om","dial":"+968"},{"name":"Panama","mask":"+507 9999-9999","iso2":"pa","dial":"+507"},{"name":"Pakistan (پاکستان‎)","mask":"+92(999) 999-9999","iso2":"pk","dial":"+92"},{"name":"Palau","mask":"+680-999-9999","iso2":"pw","dial":"+680"},{"name":"Palestinian Territory","mask":"+970 99 999 9999","iso2":"ps","dial":"+970"},{"name":"Papua New Guinea","mask":"+675(999) 99-999","iso2":"pg","dial":"+675"},{"name":"Paraguay","mask":"+595(999) 999-999","iso2":"py","dial":"+595"},{"name":"Peru (Perú)","mask":"+51(999) 999-999","iso2":"pe","dial":"+51"},{"name":"Philippines","mask":"+63(999) 999-9999","iso2":"ph","dial":"+63"},{"name":"Poland (Polska)","mask":"+48(999) 999-999","iso2":"pl","dial":"+48"},{"name":"Portugal","mask":"+351-99-999-9999","iso2":"pt","dial":"+351"},{"name":"Qatar (قطر‎)","mask":"+974-9999-9999","iso2":"qa","dial":"+974"},{"name":"Romania (România)","mask":"+40-99-999-9999","iso2":"ro","dial":"+40"},{"name":"Russian Federation (Российская Федерация)","mask":"+7(999) 999-99-99","iso2":"ru","dial":"+7"},{"name":"Rwanda","mask":"+250(999) 999-999","iso2":"rw","dial":"+250"},{"name":"Saint Kitts and Nevis","mask":"+1 (869)999-9999","iso2":"kn","dial":"+1 (869)"},{"name":"Saint Lucia","mask":"+1 (758)999-9999","iso2":"lc","dial":"+1 (758)"},{"name":"Saint Vincent and the Grenadines","mask":"+1 (784)999-9999","iso2":"vc","dial":"+1 (784)"},{"name":"Samoa","mask":"+685-99-9999","iso2":"ws","dial":"+685"},{"name":"San Marino","mask":"+378-9999-999999","iso2":"sm","dial":"+378"},{"name":"Sao Tome and Principe (São Tomé e Príncipe)","mask":"+239-99-99999","iso2":"st","dial":"+239"},{"name":"Saudi Arabia (المملكة العربية السعودية‎)","mask":"+966-9-9999-9999","iso2":"sa","dial":"+966"},{"name":"Senegal (Sénégal)","mask":"+221-99-999-9999","iso2":"sn","dial":"+221"},{"name":"Serbia (Србија)","mask":"+381-99-999-9999","iso2":"rs","dial":"+381"},{"name":"Seychelles","mask":"+248-9-999-999","iso2":"sc","dial":"+248"},{"name":"Sierra Leone","mask":"+232-99-999999","iso2":"sl","dial":"+232"},{"name":"Singapore","mask":"+65-9999-9999","iso2":"sg","dial":"+65"},{"name":"Slovakia (Slovensko)","mask":"+421(999) 999-999","iso2":"sk","dial":"+421"},{"name":"Slovenia (Slovenija)","mask":"+386-99-999-999","iso2":"si","dial":"+386"},{"name":"Solomon Islands","mask":"+677-999-9999","iso2":"sb","dial":"+677"},{"name":"Somalia (Soomaaliya)","mask":"+252-99-999-999","iso2":"so","dial":"+252"},{"name":"South Africa","mask":"+27-99-999-9999","iso2":"za","dial":"+27"},{"name":"South Korea (대한민국)","mask":"+82-99-9999-9999","iso2":"kr","dial":"+82"},{"name":"South Sudan (جنوب السودان‎)","mask":"+211-99-999-9999","iso2":"ss","dial":"+211"},{"name":"Spain (España)","mask":"+34(999) 999-999","iso2":"es","dial":"+34"},{"name":"Sri Lanka (ශ්‍රී ලංකාව)","mask":"+94-99-999-9999","iso2":"lk","dial":"+94"},{"name":"Sudan (السودان‎)","mask":"+249-99-999-9999","iso2":"sd","dial":"+249"},{"name":"Suriname","mask":"+597-999-9999","iso2":"sr","dial":"+597"},{"name":"Swaziland","mask":"+268-99-99-9999","iso2":"sz","dial":"+268"},{"name":"Sweden (Sverige)","mask":"+46-99-999-9999","iso2":"se","dial":"+46"},{"name":"Switzerland (Schweiz)","mask":"+41-99-999-9999","iso2":"ch","dial":"+41"},{"name":"Syria (سوريا‎)","mask":"+963-99-9999-999","iso2":"sy","dial":"+963"},{"name":"Taiwan (台灣)","mask":"+886-9999-9999","iso2":"tw","dial":"+886"},{"name":"Tajikistan","mask":"+992-99-999-9999","iso2":"tj","dial":"+992"},{"name":"Tanzania","mask":"+255-99-999-9999","iso2":"tz","dial":"+255"},{"name":"Thailand (ไทย)","mask":"+66-99-999-9999","iso2":"th","dial":"+66"},{"name":"Togo","mask":"+228-99-999-999","iso2":"tg","dial":"+228"},{"name":"Tonga","mask":"+676-99999","iso2":"to","dial":"+676"},{"name":"Trinidad and Tobago","mask":"+1 (868)999-9999","iso2":"tt","dial":"+1 (868)"},{"name":"Tunisia (تونس‎)","mask":"+216-99-999-999","iso2":"tn","dial":"+216"},{"name":"Turkey (Türkiye)","mask":"+90(999) 999-99999","iso2":"tr","dial":"+90"},{"name":"Turkmenistan","mask":"+993-9-999-9999","iso2":"tm","dial":"+993"},{"name":"Tuvalu","mask":"+688-999999","iso2":"tv","dial":"+688"},{"name":"Uganda","mask":"+256(999) 999-999","iso2":"ug","dial":"+256"},{"name":"Ukraine (Україна)","mask":"+380(99) 999-99-99","iso2":"ua","dial":"+380"},{"name":"United Arab Emirates (الإمارات العربية المتحدة‎)","mask":"+971-99-999-9999","iso2":"ae","dial":"+971"},{"name":"United Kingdom","mask":"+44-99-9999-99999","iso2":"gb","dial":"+44"},{"name":"USA","mask":"+1(999) 999-9999","iso2":"us","dial":"+1"},{"name":"Uruguay","mask":"+598-9-999-99-99","iso2":"uy","dial":"+598"},{"name":"Uzbekistan (Oʻzbekiston)","mask":"+998-99-999-9999","iso2":"uz","dial":"+998"},{"name":"Vanuatu","mask":"+678-99-99999","iso2":"vu","dial":"+678"},{"name":"Vatican City (Città del Vaticano)","mask":"+39-9-999-99999","iso2":"va","dial":"+39"},{"name":"Venezuela","mask":"+58(999) 999-9999","iso2":"ve","dial":"+58"},{"name":"Vietnam (Việt Nam)","mask":"+84-99-9999-999","iso2":"vn","dial":"+84"},{"name":"Yemen (اليمن‎)","mask":"+967-9-999-999","iso2":"ye","dial":"+967"},{"name":"Zambia","mask":"+260-99-999-9999","iso2":"zm","dial":"+260"},{"name":"Zimbabwe","mask":"+263-9-999999","iso2":"zw","dial":"+263"}];
const RUSSIA=COUNTRIES.find(function(c){return c.iso2==='ru';});
const UTM_KEYS=['utm_source','utm_medium','utm_campaign','utm_content','utm_term','utm_id','gclid','yclid','ysclid'];
let overlay=null,lastOpener=null;
function flag(iso){
 const node=document.createElement('span');
 node.className='prep-lead-country-flag'+(iso==='ru'?' is-ru':' is-emoji');
 node.setAttribute('aria-hidden','true');
 if(iso!=='ru'){
  const code=String(iso||'').toUpperCase();
  node.textContent=code.length===2?String.fromCodePoint(...Array.from(code).map(function(c){return c.charCodeAt(0)+127397;})):'🌐';
 }
 return node;
}
function maskInfo(c){
 const pattern=String(c.mask||'').slice(String(c.dial).length).replace(/^[\s-]+/,'');
 return {pattern:pattern,count:(pattern.match(/9/g)||[]).length};
}
function formatNational(v,c){
 const meta=maskInfo(c),max=meta.count||15,dd=String(c.dial).replace(/\D/g,'');
 let digits=String(v||'').replace(/\D/g,'');
 if(c.iso2==='ru'&&digits.length===11&&(digits[0]==='8'||digits[0]==='7'))digits=digits.slice(1);
 else if(dd&&digits.startsWith(dd)&&digits.length>max)digits=digits.slice(dd.length);
 digits=digits.slice(0,max);
 let out='',k=0;
 for(const ch of meta.pattern){
  if(ch==='9'){if(k===digits.length)break;out+=digits[k++];}
  else if(k>0||digits.length>0)out+=ch;
 }
 return out||digits;
}
function createPhone(form){
 const wrap=form.querySelector('.prep-lead-phone'),toggle=wrap.querySelector('.prep-lead-country-button');
 const input=wrap.querySelector('.prep-lead-phone-input'),menu=wrap.querySelector('.prep-lead-country-menu');
 const icon=wrap.querySelector('.prep-lead-flag-holder'),dial=wrap.querySelector('.prep-lead-country-code');
 let current=RUSSIA;
 function select(c){
  current=c;icon.replaceChildren(flag(c.iso2));dial.textContent=c.dial;
  input.placeholder=maskInfo(c).pattern.replace(/9/g,'0');
  input.value=formatNational(input.value,c);
  input.setAttribute('aria-label','Телефон: '+c.name+' '+c.dial);
  wrap.classList.remove('is-invalid');
 }
 function close(){menu.classList.remove('is-open');toggle.setAttribute('aria-expanded','false');}
 function open(){
  if(!menu.childElementCount){
   const frag=document.createDocumentFragment();
   COUNTRIES.forEach(function(c){
    const item=document.createElement('button');item.type='button';item.className='prep-lead-country-option';
    item.setAttribute('role','option');
    const name=document.createElement('span');name.className='prep-lead-country-name';name.textContent=c.name;
    const code=document.createElement('strong');code.textContent=c.dial;
    item.append(flag(c.iso2),name,code);
    item.addEventListener('click',function(){select(c);close();input.focus();form.dispatchEvent(new Event('prep:phone-change'));});
    frag.appendChild(item);
   });
   menu.appendChild(frag);
  }
  menu.classList.add('is-open');toggle.setAttribute('aria-expanded','true');
 }
 toggle.addEventListener('click',function(){menu.classList.contains('is-open')?close():open();});
 input.addEventListener('input',function(){input.value=formatNational(input.value,current);wrap.classList.remove('is-invalid');form.dispatchEvent(new Event('prep:phone-change'));});
 document.addEventListener('click',function(e){if(!wrap.contains(e.target))close();});
 menu.addEventListener('keydown',function(e){if(e.key==='Escape'){close();toggle.focus();}});
 select(RUSSIA);
 return {input:input,wrap:wrap,
  normalized:function(){const n=input.value.replace(/\D/g,'');return n?'+'+current.dial.replace(/\D/g,'')+n:'';},
  valid:function(){const len=input.value.replace(/\D/g,'').length,expected=maskInfo(current).count,total=len+current.dial.replace(/\D/g,'').length;return len>0&&total>=7&&total<=15&&(!expected||len===expected);},
  iso:function(){return current.iso2;},
  reset:function(){input.value='';select(RUSSIA);}
 };
}
function readTracking(){
 const p=new URLSearchParams(location.search),out={};
 UTM_KEYS.forEach(function(k){const v=p.get(k);if(v)out[k]=v.slice(0,500);});
 return out;
}
function createForm(mode,prefill){
 const shell=document.createElement('div');shell.className='prep-lead-shell';
 const form=document.createElement('form');form.className='prep-lead-form';form.noValidate=true;
 form.innerHTML="\n<div class=\"prep-lead-field\"><label class=\"prep-label\">Ваше имя<input class=\"prep-lead-input\" name=\"full_name\" type=\"text\" maxlength=\"180\" autocomplete=\"name\" placeholder=\"Как к вам обращаться\" required></label></div>\n<div class=\"prep-lead-field\"><label class=\"prep-label\">Телефон</label><div class=\"prep-lead-phone\">\n<button type=\"button\" class=\"prep-lead-country-button\" aria-label=\"Выбрать страну\" aria-haspopup=\"listbox\" aria-expanded=\"false\"><span class=\"prep-lead-flag-holder\"></span><span class=\"prep-lead-country-code\">+7</span><span class=\"prep-lead-country-chevron\" aria-hidden=\"true\">▾</span></button>\n<input class=\"prep-lead-input prep-lead-phone-input\" type=\"tel\" name=\"phone_national\" inputmode=\"tel\" autocomplete=\"tel-national\" placeholder=\"(000) 000-00-00\">\n<div class=\"prep-lead-country-menu\" role=\"listbox\" aria-label=\"Коды стран\"></div></div></div>\n<div class=\"prep-lead-field prep-lead-wide\"><label class=\"prep-label\">Email (необязательно, если указан телефон)<input class=\"prep-lead-input\" name=\"email\" type=\"email\" autocomplete=\"email\" maxlength=\"254\" placeholder=\"name@example.ru\"></label></div>\n<fieldset class=\"prep-lead-method\"><legend>Как с вами удобнее связаться?</legend><div class=\"prep-lead-method-options\">\n<label class=\"prep-lead-method-option\"><input type=\"radio\" name=\"preferred_contact\" value=\"phone\"><span>Звонок</span></label>\n<label class=\"prep-lead-method-option\"><input type=\"radio\" name=\"preferred_contact\" value=\"telegram\"><span>Telegram</span></label>\n<label class=\"prep-lead-method-option\"><input type=\"radio\" name=\"preferred_contact\" value=\"whatsapp\"><span>WhatsApp</span></label>\n<label class=\"prep-lead-method-option\"><input type=\"radio\" name=\"preferred_contact\" value=\"email\"><span>Email</span></label>\n</div></fieldset>\n<div class=\"prep-lead-field prep-lead-wide\"><label class=\"prep-label\">Комментарий (необязательно)<textarea class=\"prep-lead-textarea\" name=\"comment\" maxlength=\"3000\" placeholder=\"Какие товары и объем партии? Для какого маркетплейса нужна подготовка?\"></textarea></label></div>\n<div class=\"prep-lead-honeypot\" aria-hidden=\"true\"><label>Веб-сайт<input name=\"company_website\" type=\"text\" tabindex=\"-1\" autocomplete=\"off\"></label></div>\n<div class=\"prep-lead-action\"><button class=\"prep-lead-submit\" type=\"submit\">Отправить заявку</button></div>\n<p class=\"prep-lead-status\" role=\"status\" aria-live=\"polite\"></p>\n<p class=\"prep-lead-consent\">Нажимая «Отправить заявку», вы соглашаетесь с <a href=\"/privacy-policy/\">политикой обработки персональных данных</a>.</p>";
 shell.appendChild(form);
 const name=form.elements.full_name,email=form.elements.email,comment=form.elements.comment;
 const hp=form.elements.company_website,submit=form.querySelector('.prep-lead-submit');
 const status=form.querySelector('.prep-lead-status'),phone=createPhone(form);
 const methods=Array.from(form.querySelectorAll('[name="preferred_contact"]'));
 if(prefill)comment.value=prefill.slice(0,3000);
 let startTime=Date.now();
 function method(){const m=methods.find(function(el){return el.checked;});return m?m.value:'';}
 function update(){
  const hasPhone=!!phone.input.value.trim(),hasEmail=!!email.value.trim();
  methods.forEach(function(el){el.disabled=el.value==='email'?!hasEmail:!hasPhone;if(el.disabled)el.checked=false;});
 }
 form.addEventListener('prep:phone-change',update);email.addEventListener('input',update);update();
 function show(msg,type){status.textContent=msg||'';status.classList.toggle('is-error',type==='error');status.classList.toggle('is-success',type==='success');}
 function fallback(){
  show('Отправка через сайт пока настраивается. Обратитесь к менеджеру: ','error');
  const link=document.createElement('a');link.href='https://t.me/prepmanager2';
  link.target='_blank';link.rel='noopener';link.textContent='написать в Telegram';
  status.appendChild(link);
 }
 function validate(){
  name.removeAttribute('aria-invalid');email.removeAttribute('aria-invalid');phone.wrap.classList.remove('is-invalid');show('',null);
  if(!name.value.trim()){name.setAttribute('aria-invalid','true');name.focus();show('Укажите ваше имя.','error');return false;}
  if(!phone.input.value.trim()&&!email.value.trim()){phone.wrap.classList.add('is-invalid');phone.input.focus();show('Укажите телефон или email.','error');return false;}
  if(phone.input.value.trim()&&!phone.valid()){phone.wrap.classList.add('is-invalid');phone.input.focus();show('Проверьте номер телефона.','error');return false;}
  if(email.value.trim()&&!email.validity.valid){email.setAttribute('aria-invalid','true');email.focus();show('Проверьте email.','error');return false;}
  if(!method()){show('Выберите удобный способ связи.','error');return false;}
  return true;
 }
 form.addEventListener('submit',async function(e){
  e.preventDefault();if(submit.disabled||!validate())return;
  if(hp.value){show('Спасибо!','success');return;}
  if(!ENDPOINT){fallback();return;}
  const canonical=document.querySelector('link[rel="canonical"][href]');
  const payload={
   site:'prepcenter',lang:'ru',full_name:name.value.trim(),phone:phone.normalized(),
   phone_country:phone.iso(),email:email.value.trim(),preferred_contact:method(),contact_method:method(),
   comment:comment.value.trim(),company_website:hp.value,
   entity_id:'prepcenter:page:'+location.pathname,
   canonical_url:canonical?canonical.href:location.origin+location.pathname,
   page_url:location.href,referrer:document.referrer||'',utm:readTracking(),
   form_started_at:new Date(startTime).toISOString(),submitted_at:new Date().toISOString()
  };
  submit.disabled=true;show('Отправляем заявку...',null);
  const controller=new AbortController(),timer=setTimeout(function(){controller.abort();},12000);
  try{
   const response=await fetch(ENDPOINT,{method:'POST',credentials:'omit',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify(payload)});
   if(!response.ok)throw Error('HTTP '+response.status);
   const body=await response.json();
   if(!body||body.ok!==true)throw Error('Invalid delivery acknowledgement');
   // Successful delivery: clear personal data and restore the ready-to-send state.
   form.reset();
   phone.reset();
   name.removeAttribute('aria-invalid');
   email.removeAttribute('aria-invalid');
   phone.wrap.classList.remove('is-invalid');
   update();
   startTime=Date.now();
   submit.disabled=false;
   show('Заявка отправлена. Менеджер свяжется с вами.','success');
   document.dispatchEvent(new CustomEvent('prep:lead-success',{detail:{mode:mode}}));
   if(mode==='modal')setTimeout(closeModal,1250);
  }catch(err){submit.disabled=false;show('Не удалось отправить. Попробуйте еще раз или обратитесь к менеджеру.','error');}
  finally{clearTimeout(timer);}
 });
 shell.prepFocus=function(){name.focus();};
 return shell;
}
function inlineForm(titleText,leadText,kind){
 const section=document.createElement('section');section.className='prep-lead-section '+(kind||'');
 const container=document.createElement('div');container.className='container prep-lead-layout';
 const intro=document.createElement('div');intro.className='prep-lead-intro';
 const h=document.createElement('h2');h.textContent=titleText;
 const p=document.createElement('p');p.textContent=leadText;intro.append(h,p);
 container.append(intro,createForm('inline',''));section.appendChild(container);
 return section;
}
function mountInline(){
 document.querySelectorAll('[data-prep-inline-form]').forEach(function(container){
  if(container.querySelector('.prep-lead-shell'))return;
  container.appendChild(createForm('inline',''));
 });
 const reviews=document.getElementById('reviews'),about=document.getElementById('about');
 if(reviews&&about&&!document.getElementById('prep-lead-consultation')){
  const s=inlineForm('Оставьте свои контактные данные','Мы перезвоним вам и поможем подобрать услуги для вашей партии товаров.','prep-lead-section--after-reviews');
  s.id='prep-lead-consultation';about.insertAdjacentElement('beforebegin',s);
 }
 const faq=document.getElementById('questions');
 if(faq&&!document.getElementById('prep-lead-faq')){
  const s=inlineForm('Не нашли ответа на свой вопрос?','Задайте вопрос специалистам на бесплатной консультации.','prep-lead-section--faq');
  s.id='prep-lead-faq';faq.insertAdjacentElement('afterend',s);
 }
 if(location.pathname.replace(/\/+$/,'/')==='/contacts/'&&!document.getElementById('prep-lead-contacts')){
  const footer=document.getElementById('contact');
  if(footer){const s=inlineForm('Оставить заявку','Расскажите о товарах и задаче. Мы свяжемся с вами.','prep-lead-section--contacts');
   s.id='prep-lead-contacts';footer.insertAdjacentElement('beforebegin',s);}
 }
}
function closeModal(){
 if(!overlay)return;overlay.remove();overlay=null;
 document.body.classList.remove('prep-lead-modal-open');document.removeEventListener('keydown',modalKeydown);
 if(lastOpener&&typeof lastOpener.focus==='function')lastOpener.focus({preventScroll:true});lastOpener=null;
}
function modalKeydown(e){
 if(!overlay)return;
 if(e.key==='Escape'){e.preventDefault();closeModal();return;}
 if(e.key!=='Tab')return;
 const controls=Array.from(overlay.querySelectorAll('button:not([disabled]),input:not([disabled]),textarea,a[href]')).filter(function(x){return x.offsetParent!==null;});
 if(!controls.length)return;
 if(e.shiftKey&&document.activeElement===controls[0]){e.preventDefault();controls[controls.length-1].focus();}
 else if(!e.shiftKey&&document.activeElement===controls[controls.length-1]){e.preventDefault();controls[0].focus();}
}
function openModal(opener,prefill){
 if(overlay)return;
 lastOpener=opener||document.activeElement;
 const excursion=/экскурси/i.test((opener&&opener.textContent)||'');
 const calculatorRequest=typeof prefill==='string' && prefill.length>0;
 overlay=document.createElement('div');overlay.className='prep-lead-overlay';
 const dialog=document.createElement('div');dialog.className='prep-lead-dialog';
 dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');dialog.setAttribute('aria-labelledby','prep-lead-dialog-title');
 const close=document.createElement('button');close.type='button';close.className='prep-lead-close';close.setAttribute('aria-label','Закрыть форму');close.textContent='×';
 const title=document.createElement('h2');title.id='prep-lead-dialog-title';title.textContent=calculatorRequest?'Отправить расчет':excursion?'Записаться на экскурсию':'Оставить заявку';
 const lead=document.createElement('p');lead.className='prep-lead-modal-intro';
 lead.textContent=calculatorRequest?'Укажите, как с вами связаться. Расчет партии уже добавлен в комментарий.':excursion?'Оставьте контакты, чтобы согласовать удобное время посещения склада.':'Оставьте контакты и коротко расскажите, какой товар нужно подготовить к маркетплейсам.';
 const form=createForm('modal',calculatorRequest?prefill:excursion?'Хочу записаться на экскурсию на склад.':'');
 dialog.append(close,title,lead,form);overlay.appendChild(dialog);document.body.appendChild(overlay);
 document.body.classList.add('prep-lead-modal-open');
 close.addEventListener('click',closeModal);
 overlay.addEventListener('mousedown',function(e){if(e.target===overlay)closeModal();});
 document.addEventListener('keydown',modalKeydown);
 setTimeout(function(){if(overlay)form.prepFocus();},0);
}
function isLeadTrigger(anchor){
 if(!anchor)return false;
 const href=anchor.getAttribute('href')||'';
 if(href==='#modal'||href==='/#modal'||href==='https://prep-center.ru/#modal')return true;
 if(href!=='https://t.me/prepmanager2')return false;
 const label=(anchor.textContent||'').trim().replace(/\s+/g,' ');
 if(/telegram|рассчитать стоимость|калькулятор|расчет стоимости/i.test(label))return false;
 return /^(Начать сотрудничество|Записаться на экскурсию|Оставить заявку)$/i.test(label);
}
document.addEventListener('click',function(e){
 const a=e.target.closest&&e.target.closest('a[href]');
 if(!isLeadTrigger(a)||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
 e.preventDefault();document.querySelectorAll('.mobile-nav details[open]').forEach(function(x){x.open=false;});
 openModal(a);
});
mountInline();
window.PrepCenterLeadForm={open:openModal,close:closeModal};
})();
