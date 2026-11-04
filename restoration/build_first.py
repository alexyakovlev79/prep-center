from pathlib import Path
from lxml import html, etree
from copy import deepcopy
import json,re,hashlib

ROOT=Path(__file__).parent
SITE=ROOT.parent if (ROOT.parent/'index.html').exists() else ROOT/'site'
SOURCE=ROOT/'source'
SLUG='fulfillment-zhidkih-tovarov'
home=html.fromstring((SITE/'index.html').read_bytes())
original=html.fromstring((SOURCE/'liquid-20260822.html').read_bytes())
article=deepcopy(original.xpath('//article[@class="liquidservice"]')[0])

# Keep the original text, section structure and component CSS. Cross-check against
# the search-index copy retrieved 2026-11-04 (crawl label: "2 weeks ago").
for n,img in enumerate(article.xpath('.//img'),1):
    img.attrib.pop('srcset',None)
    img.set('src',f'../assets/liquid-{n:02}.webp')
    img.set('loading','eager' if n==1 else 'lazy')
    img.set('decoding','async')
    from PIL import Image
    w,h=Image.open(SITE/'assets'/f'liquid-{n:02}.webp').size
    img.set('width',str(w));img.set('height',str(h))
for a in article.xpath('.//a'):
    old=a.get('href','')
    a.set('data-original-href',old)
    a.set('href','#contact' if old in ['/#calc','#modal'] else '../')
    if old=='/#tariffs':a.set('data-original-href','/tarify/')

# Update CTA labels to the later indexed copy and restore a real contact route.
for a in article.xpath('.//a[@href="#contact"]'):
    if a.getparent().get('class')=='liquidservice__links':
        a.text='Обсудить партию жидких товаров'
        tg=etree.Element('a',href='https://t.me/prepmanager2',attrib={'class':'liquidservice__text-link'})
        tg.text='Написать в Telegram';a.addnext(tg)

head=deepcopy(home.xpath('//head')[0])
head.xpath('./title')[0].text=original.xpath('//title')[0].text
for m in head.xpath('./meta[@name="description"]'):
    m.set('content',original.xpath('//meta[@name="description"]/@content')[0])
head.xpath('./link[@rel="canonical"]')[0].set('href',f'https://prep-center.ru/{SLUG}/')
for node in head.xpath('.//*[@href]'):
    if node.get('href','').startswith('./assets/'):node.set('href','.'+node.get('href'))
for n in head.xpath('./link[@rel="preload"][@as="image"]'):n.set('href','../assets/liquid-01.webp')
css=etree.SubElement(head,'link',rel='stylesheet',href='../assets/liquid-service.css')
header=deepcopy(home.xpath('//header')[0])
contact=deepcopy(home.xpath('//*[@id="contact"]')[0])
for block in [header,contact]:
    for a in block.xpath('.//a'):
        a.set('href','../fulfillment-zhidkih-tovarov/' if a.text=='Фулфилмент' else '../')
    for im in block.xpath('.//img'):
        if im.get('src','').startswith('./assets/'):im.set('src','.'+im.get('src'))
for a in contact.xpath('.//a'):
    label=' '.join(a.text_content().split())
    if label.startswith('+7'):a.set('href','tel:+79306007520')
    elif label=='info@prep-center.ru':a.set('href','mailto:info@prep-center.ru')
    elif 'Telegram:' in label or 'экскурсию' in label:a.set('href','https://t.me/prepmanager2')
for a in header.xpath('.//a'):
    label=' '.join(a.text_content().split())
    if label.startswith('+7'):a.set('href','tel:+79306007520')
    elif label=='info@prep-center.ru':a.set('href','mailto:info@prep-center.ru')
    elif label=='Обсудить задачу':a.set('href','#contact')

doc=etree.Element('html',lang='ru');doc.append(head)
body=etree.SubElement(doc,'body');body.append(header)
main=etree.SubElement(body,'main');main.append(article);main.append(contact)
for script in original.xpath('//script[@type="application/ld+json"]'):
    data=json.loads(script.text)
    if data.get('@type') in ['Service','FAQPage','BreadcrumbList']:
        el=etree.SubElement(body,'script',type='application/ld+json')
        el.text=json.dumps(data,ensure_ascii=False,separators=(',',':'))
target=SITE/SLUG/'index.html';target.parent.mkdir(exist_ok=True)
target.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html')+'\n')

css=(SOURCE/'liquid-inline.css').read_text()+'''
/* Recovered page styles; common header/footer come from the homepage. */
.liquidservice li{margin-bottom:.55em}.liquidservice ul:not(.liquidservice__facts),.liquidservice ol{padding-left:1.35em;margin:0 0 24px}.liquidservice li::marker{color:#ff9800;font-weight:700}.liquidservice__facts{list-style:none}.liquidservice__facts li{margin:0}.liquidservice__hero>*,.liquidservice__split>*{min-width:0}.liquidservice img{height:auto}.liquidservice summary::marker{color:#ff9800}.liquidservice details[open] summary{color:#a65d00}.liquidservice a:focus-visible{outline:3px solid #ff9800;outline-offset:4px}.liquidservice__final a:not(.liquidservice__button){color:#fff}.liquidservice__hero h1{font-family:Bebas,sans-serif}.liquidservice h3{font-family:Tilda,sans-serif;font-weight:600}.liquidservice__date{font-size:14px;color:#5d6c7d;margin-bottom:20px}
@media(max-width:640px){.liquidservice h1{font-size:34px;overflow-wrap:break-word}.liquidservice__button{white-space:normal}.liquidservice__breadcrumbs{font-size:14px}}
'''
(SITE/'assets/liquid-service.css').write_text(css+'\n/* Reserve visible widths for lazy portrait images. */\n.liquidservice__photo-pair img{width:min(100%,390px);height:auto;max-height:none}.liquidservice__content-image,.liquidservice__split img{width:min(100%,650px);height:auto;max-height:none}\n')

# A single navigation link activates the first restored page. Other homepage
# links retain the user's temporary homepage fallback.
for a in home.xpath('//a'):
    if ' '.join(a.text_content().split())=='Фулфилмент':a.set('href','./'+SLUG+'/')
(SITE/'index.html').write_text('<!doctype html>\n'+html.tostring(home,encoding='unicode',method='html')+'\n')

provenance={
 'page':f'https://prep-center.ru/{SLUG}/',
 'retrieved_on':'2026-11-04',
 'latest_indexed_copy':{'crawl_label':'2 weeks ago','exact_capture_date':None,'content_date':'2026-08-21','note':'Relative crawl label is consistent with late October 2026; exact date is not verified. Main text was compared with the complete saved HTML.'},
 'complete_html_snapshot_date':'2026-08-22',
 'source_html_sha256':hashlib.sha256((SOURCE/'liquid-20260822.html').read_bytes()).hexdigest(),
 'visual_assets':{'original_files':6,'generated_now':0,'hero':'Existing illustrative cover; not a real warehouse photograph.'},
 'functionality':{'faq':'Native details/summary restored','contact':'Phone, email and Telegram links work','forms':'Server-side submission is not restored; CTA opens contacts','internal_links':'Unrestored destinations temporarily point to the homepage; original paths retained in data-original-href'},
 'shared_components':'Generated from the current root index.html; no separate manually edited header/footer source.'
}
(SOURCE/'first-page-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
print(json.dumps({'page':str(target),'bytes':target.stat().st_size,'images':len(article.xpath('.//img')),'faq':len(article.xpath('.//details'))},ensure_ascii=False))
