from pathlib import Path
from lxml import html,etree
from copy import deepcopy
from PIL import Image
import json,re

R=Path(__file__).parent; S=R/'source'
SITE=R.parent if (R.parent/'index.html').exists() else R/'site'
PAGES=[('fulfillment-fbo','fboservice','fbo',7),('fulfillment-fbs','fbsservice','fbs',8),('termousadka-vpp','packservice','pack',5)]
LIVE={'/','/fulfillment-zhidkih-tovarov/','/fulfillment-fbo/','/fulfillment-fbs/','/termousadka-vpp/'}
home=html.fromstring((SITE/'index.html').read_bytes())
def label(e):return ' '.join(' '.join(e.itertext()).split())
def set_fragment(e,s):
    e.clear()
    for f in html.fragments_fromstring(s):
        if isinstance(f,str):e.text=(e.text or '')+f
        else:e.append(f)
def section(a,heading):return next(e.getparent() for e in a.xpath('.//h2') if label(e)==heading)
def relative(path,home_page=False):
    base='.' if home_page else '..'
    return base+path
def resolve_links(block,home_page=False):
    for a in block.xpath('.//a'):
        old=a.get('data-original-href',a.get('href',''))
        if old.startswith(('tel:','mailto:','https://t.me/')):continue
        if old=='#modal':a.set('href','#contact');a.set('data-original-href',old);continue
        if old.startswith('https://prep-center.ru'):old=old[len('https://prep-center.ru'):]
        if old.startswith('/'):
            a.set('data-original-href',old)
            path=old.split('#')[0] or '/';anchor=('#'+old.split('#',1)[1]) if '#' in old else ''
            if path=='/' and anchor in ['#modal','#calc']:a.set('href','#contact')
            elif path in LIVE:a.set('href',relative(path,home_page)+anchor)
            else:a.set('href','./' if home_page else '../')
def common(block):
    out=deepcopy(block)
    for im in out.xpath('.//img'):
        src=im.get('src','')
        if src.startswith('./assets/'):im.set('src','.'+src)
    for a in out.xpath('.//a'):
        t=label(a)
        if t.startswith('+7'):a.set('href','tel:+79306007520')
        elif t=='info@prep-center.ru':a.set('href','mailto:info@prep-center.ru')
        elif 'Telegram:' in t or t=='Записаться на экскурсию':a.set('href','https://t.me/prepmanager2')
        elif t=='Обсудить задачу':a.set('href','#contact')
        elif t=='Услуги':a.set('href','../termousadka-vpp/')
        elif t=='Фулфилмент':a.set('href','../fulfillment-zhidkih-tovarov/')
        else:a.set('href','../')
    return out

# Keep one canonical source for the current common components: root index.html.
for a in home.xpath('//a'):
    t=label(a)
    if t=='Услуги':a.set('href','./termousadka-vpp/')
    elif t=='FBO':a.set('href','./fulfillment-fbo/')
    elif t=='FBS':a.set('href','./fulfillment-fbs/')
    elif t=='Упаковка товаров':a.set('href','./termousadka-vpp/')
(SITE/'index.html').write_text('<!doctype html>\n'+html.tostring(home,encoding='unicode',method='html')+'\n')
header=home.xpath('//header')[0];contact=home.xpath('//*[@id="contact"]')[0]
provenance=[]
for slug,cls,prefix,count in PAGES:
    source=html.fromstring((S/(slug+'-20260822.html')).read_bytes());a=deepcopy(source.xpath('//article')[0])
    if slug=='fulfillment-fbs':
        # Confirmed additions in the indexed copy updated on 20 October 2026.
        h=section(a,'Современная WMS для FBS')
        p=next(e for e in h.xpath('.//p') if 'В Преп-Центре используется' in label(e))
        set_fragment(p,'В Преп-Центре используется <a href="/wms-mpfit-dlya-fulfillmenta/">WMS МПФИТ для FBS</a> с интеграциями с маркетплейсами.')
        h=section(a,'Упаковка и маркировка FBS-заказов')
        p=html.fromstring('<p>Когда дополнительная пленка или пакет закрывают заводской DataMatrix, <a href="/chestnyy-znak/">повторно печатаем КИЗ той же единицы для внешней упаковки</a>. Сканирование и нанесение включаем в согласованный регламент обработки FBS-заказа.</p>');h.insert(1,p)
        cards=html.fromstring('''<section class="fbsservice__section"><h2>FBS для вашего маркетплейса</h2><p>Выберите площадку, чтобы посмотреть схему работы, упаковку, передачу заказов и ответы на частые вопросы.</p><div class="fbsservice__cards"><div class="fbsservice__card"><h3><a href="/fbs-wildberries/">FBS для Wildberries</a></h3><p>Хранение, сборка, маркировка и регулярная передача заказов WB.</p></div><div class="fbsservice__card"><h3><a href="/fbs-ozon/">FBS для Ozon</a></h3><p>Обработка заказов «с моих складов» и передача в логистику Ozon.</p></div><div class="fbsservice__card"><h3><a href="/fbs-yandex-market/">FBS для Яндекс Маркета</a></h3><p>Сборка и передача заказов в доступную точку приема или машину Маркета.</p></div></div></section>''')
        anchor=section(a,'Как работает FBS через Преп-Центр');anchor.addprevious(cards)
        requirements=html.fromstring('''<section class="fbsservice__section"><h2>Требования FBS по маркетплейсам</h2><div class="fbsservice__cards"><div class="fbsservice__card"><h3><a href="/trebovaniya-fbs-wildberries/">Правила FBS Wildberries</a></h3></div><div class="fbsservice__card"><h3><a href="/trebovaniya-fbs-ozon/">Правила FBS Ozon</a></h3></div><div class="fbsservice__card"><h3><a href="/trebovaniya-fbs-yandex-market/">Правила FBS Яндекс Маркета</a></h3></div></div></section>''')
        section(a,'Вопросы об FBS-фулфилменте').addprevious(requirements)
    if slug=='fulfillment-fbo':
        for row in a.xpath('.//table//tr'):
            cells=row.xpath('./td')
            if len(cells)!=2:continue
            t=label(cells[0])
            if t.startswith('Подготовка короба 60'):cells[1].text='150 ₽ / короб'
            elif t.startswith('Паллетирование:'):cells[1].text='400 ₽ / паллет'
        # The 500-ruble pallet-supply tariff is a separate operation and stays.
    images=a.xpath('.//img');assert len(images)==count
    for i,im in enumerate(images,1):
        path=SITE/'assets'/f'{prefix}-{i:02}.webp';w,h=Image.open(path).size
        for attr in ['srcset','data-src','data-srcset']:im.attrib.pop(attr,None)
        im.set('src',f'../assets/{prefix}-{i:02}.webp');im.set('width',str(w));im.set('height',str(h));im.set('loading','eager' if i==1 else 'lazy');im.set('decoding','async');im.set('style',(im.get('style','')+';aspect-ratio:'+str(w)+' / '+str(h)).lstrip(';'))
    # The server-side form is unavailable. Contact CTAs lead to real contacts.
    for el in a.xpath('.//*[@onclick or @data-modal]'):
        el.attrib.pop('onclick',None);el.attrib.pop('data-modal',None)
    resolve_links(a)
    for link in a.xpath('.//a[contains(@href,"#contact")]'):
        t=label(link)
        if 'Рассчитать' in t:link.text='Обсудить FBO-поставку' if prefix=='fbo' else 'Обсудить FBS' if prefix=='fbs' else 'Обсудить упаковку'
    css=source.xpath('//main/style')[0].text
    css+=f'''\n/* Adaptation to the shared recovery shell; original page component layout preserved. */
.{cls} li{{margin-bottom:.5em}}.{cls} ul,.{cls} ol{{padding-left:1.35em;margin:0 0 24px}}.{cls} li::marker{{color:#ff9800;font-weight:700}}.{cls}__highlights,.{cls}__facts{{list-style:none;padding:0!important}}.{cls}__highlights li,.{cls}__facts li{{margin:0}}.{cls}__hero>*,.{cls}__split>*{{min-width:0}}.{cls} img{{height:auto}}.{cls} h3{{font-family:Tilda,sans-serif}}.{cls} a:focus-visible{{outline:3px solid #ff9800;outline-offset:4px}}.{cls}__recovery-date{{font-size:14px;color:#5e6b78;margin:0 0 18px}}.{cls}__faq summary::marker{{color:#ff9800}}.{cls}__photo-pair img{{width:min(100%,390px);height:auto;max-height:none}}
@media(max-width:640px){{.{cls} h1{{overflow-wrap:break-word}}.{cls}__button{{white-space:normal}}}}
'''
    if prefix=='pack':css+='\n@media(max-width:640px){.packservice__compare th:first-child,.packservice__compare td:first-child{width:42%}.packservice__compare th:not(:first-child),.packservice__compare td:not(:first-child){width:29%}}\n'
    (SITE/'assets'/f'{slug}.css').write_text(css)
    head=deepcopy(home.xpath('//head')[0]);head.xpath('./title')[0].text=source.xpath('//title')[0].text
    for m in head.xpath('./meta[@name="description"]'):m.set('content',source.xpath('//meta[@name="description"]/@content')[0])
    head.xpath('./link[@rel="canonical"]')[0].set('href',f'https://prep-center.ru/{slug}/')
    for n in head.xpath('.//*[@href]'):
        if n.get('href','').startswith('./assets/'):n.set('href','.'+n.get('href'))
    for n in head.xpath('./link[@rel="preload"][@as="image"]'):n.set('href',f'../assets/{prefix}-01.webp')
    etree.SubElement(head,'link',rel='stylesheet',href=f'../assets/{slug}.css')
    doc=etree.Element('html',lang='ru');doc.append(head);body=etree.SubElement(doc,'body');body.append(common(header));main=etree.SubElement(body,'main');main.append(a);main.append(common(contact))
    nodes=[]
    for sc in source.xpath('//script[@type="application/ld+json"]'):
        j=json.loads(sc.text);nodes+=j.get('@graph',[j])
    for j in nodes:
        if j.get('@type') not in ['Service','BreadcrumbList']:continue
        sc=etree.SubElement(body,'script',type='application/ld+json');sc.text=json.dumps(j,ensure_ascii=False,separators=(',',':'))
    faq=[]
    for item in a.xpath('.//details'):
        summary=item.xpath('./summary');ans=item.xpath('./*[not(self::summary)]')
        if summary:faq.append({'@type':'Question','name':label(summary[0]),'acceptedAnswer':{'@type':'Answer','text':' '.join(label(x) for x in ans)}})
    if faq:
        sc=etree.SubElement(body,'script',type='application/ld+json');sc.text=json.dumps({'@context':'https://schema.org','@type':'FAQPage','mainEntity':faq},ensure_ascii=False,separators=(',',':'))
    out=SITE/slug/'index.html';out.parent.mkdir(exist_ok=True);out.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html')+'\n')
    provenance.append({'slug':slug,'complete_html_date':'2026-08-22','latest_evidence':'Indexed copy updated 2026-10-20, main text compared; October marketplace blocks and WMS/KIZ additions restored' if prefix=='fbs' else 'Indexed copy says updated 2026-09-18; complete October HTML not found; confirmed 2026-10-20 box and palletization prices applied' if prefix=='fbo' else 'Index result says updated 2026-08-21; a previous index response reported crawl last week, exact capture unavailable; no later body snapshot obtained','images':count,'faq':len(faq),'new_images_generated':0,'limitations':'Unrestored internal destinations temporarily point to homepage; contact route replaces server-side form'})

# Refresh existing internal page navigation and activate all four recovered routes.
p=SITE/'fulfillment-zhidkih-tovarov/index.html';d=html.fromstring(p.read_bytes());d.xpath('//header')[0].getparent().replace(d.xpath('//header')[0],common(header));old=d.xpath('//*[@id="contact"]')[0];old.getparent().replace(old,common(contact));resolve_links(d.xpath('//article')[0]);[n.set('href','../assets/liquid-01.webp') for n in d.xpath('//head/link[@rel="preload"][@as="image"]')];p.write_text('<!doctype html>\n'+html.tostring(d,encoding='unicode',method='html')+'\n')
(S/'batch3-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2));print(json.dumps(provenance,ensure_ascii=False))
