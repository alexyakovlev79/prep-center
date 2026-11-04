from pathlib import Path
from lxml import html,etree
from copy import deepcopy
from PIL import Image
import json,re

R=Path(__file__).parent; S=R/'source'
SITE=R.parent if (R.parent/'index.html').exists() else R/'site'
PAGES=[('chestnyy-znak','czservice','cz',4),('etiketki-marketpleysov','labelsservice','labels',4),('komplektatsiya-naborov','kitservice','kits',5)]
LIVE={'/','/fulfillment-zhidkih-tovarov/','/fulfillment-fbo/','/fulfillment-fbs/','/termousadka-vpp/','/chestnyy-znak/','/etiketki-marketpleysov/','/komplektatsiya-naborov/'}
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
        elif a.get('data-original-href','').split('#')[0] in LIVE:a.set('href','..'+a.get('data-original-href'))
        else:a.set('href','../')
    return out

# Activate only recovered destinations in the canonical homepage.
for link in home.xpath('//a'):
    target={'Маркировка и учет':'/chestnyy-znak/','Маркировка товаров':'/etiketki-marketpleysov/','комплектуем наборы':'/komplektatsiya-naborov/'}.get(label(link))
    if target:link.set('href','.'+target);link.set('data-original-href',target)
(SITE/'index.html').write_text('<!doctype html>\n'+html.tostring(home,encoding='unicode',method='html')+'\n')
header=home.xpath('//header')[0];contact=home.xpath('//*[@id="contact"]')[0]
provenance=[]
for slug,cls,prefix,count in PAGES:
    source=html.fromstring((S/(slug+'-20260822.html')).read_bytes());a=deepcopy(source.xpath('//article')[0])
    if prefix=='cz':
        block=section(a,'Работа с КИЗ через WMS МПФИТ')
        note=next(p for p in block.xpath('.//p') if 'На странице не используются' in label(p))
        set_fragment(note,'Как эта же система используется для остатков, FBO/FBS, биллинга и других процессов, показали в материале <a href="/wms-mpfit-dlya-fulfillmenta/">как мы используем WMS МПФИТ в Преп-Центре</a>.')
    images=a.xpath('.//img');assert len(images)==count
    for i,im in enumerate(images,1):
        asset_i=[1,3,4,2,5][i-1] if prefix=='kits' else i
        path=SITE/'assets'/f'{prefix}-{asset_i:02}.webp';w,h=Image.open(path).size
        for attr in ['srcset','data-src','data-srcset']:im.attrib.pop(attr,None)
        im.set('src',f'../assets/{prefix}-{asset_i:02}.webp');im.set('width',str(w));im.set('height',str(h));im.set('loading','eager' if i==1 else 'lazy');im.set('decoding','async');im.set('style',(im.get('style','')+';aspect-ratio:'+str(w)+' / '+str(h)).lstrip(';'))
    # The server-side form is unavailable. Contact CTAs lead to real contacts.
    for el in a.xpath('.//*[@onclick or @data-modal]'):
        el.attrib.pop('onclick',None);el.attrib.pop('data-modal',None)
    resolve_links(a)
    css=source.xpath('//main/style')[0].text
    css+=f'''\n/* Adaptation to the shared recovery shell; original page component layout preserved. */
.{cls} li{{margin-bottom:.5em}}.{cls} ul,.{cls} ol{{padding-left:1.35em;margin:0 0 24px}}.{cls} li::marker{{color:#ff9800;font-weight:700}}.{cls}__highlights,.{cls}__facts{{list-style:none;padding:0!important}}.{cls}__highlights li,.{cls}__facts li{{margin:0}}.{cls}__hero>*,.{cls}__split>*{{min-width:0}}.{cls} img{{height:auto}}.{cls} h3{{font-family:Tilda,sans-serif}}.{cls} a:focus-visible{{outline:3px solid #ff9800;outline-offset:4px}}.{cls}__recovery-date{{font-size:14px;color:#5e6b78;margin:0 0 18px}}.{cls}__faq summary::marker{{color:#ff9800}}.{cls}__photo-pair img{{width:min(100%,390px);height:auto;max-height:none}}.{cls}__split img{{width:min(100%,650px);height:auto!important;max-height:none}}
@media(max-width:640px){{.{cls} h1{{overflow-wrap:break-word}}.{cls}__button{{white-space:normal}}}}
'''
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
        j={'@context':'https://schema.org',**j}
        sc=etree.SubElement(body,'script',type='application/ld+json');sc.text=json.dumps(j,ensure_ascii=False,separators=(',',':'))
    faq=[]
    for item in a.xpath('.//details'):
        summary=item.xpath('./summary');ans=item.xpath('./*[not(self::summary)]')
        if summary:faq.append({'@type':'Question','name':label(summary[0]),'acceptedAnswer':{'@type':'Answer','text':' '.join(label(x) for x in ans)}})
    if faq:
        sc=etree.SubElement(body,'script',type='application/ld+json');sc.text=json.dumps({'@context':'https://schema.org','@type':'FAQPage','mainEntity':faq},ensure_ascii=False,separators=(',',':'))
    out=SITE/slug/'index.html';out.parent.mkdir(exist_ok=True);out.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html')+'\n')
    provenance.append({'slug':slug,'complete_html_date':'2026-08-22','latest_evidence':'Indexed copy checked 2026-11-04; published update date remains August; complete October snapshot not obtained','images':count,'faq':len(faq),'new_images_generated':0,'limitations':'Contact route replaces server-side form; unrestored pages point to homepage'})
(S/'next3-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
print(json.dumps(provenance,ensure_ascii=False))

# Resolve recovered article destinations on existing pages without redesigning them.
for slug in ['fulfillment-zhidkih-tovarov','fulfillment-fbo','fulfillment-fbs','termousadka-vpp']:
    path=SITE/slug/'index.html';doc=html.fromstring(path.read_bytes());resolve_links(doc.xpath('//article')[0]);path.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html')+'\n')
