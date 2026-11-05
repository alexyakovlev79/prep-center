"""Restore the remaining routes from retained HTML, October sources and price data."""
from pathlib import Path
from copy import deepcopy
from urllib.parse import urlsplit, urljoin, unquote
from lxml import html, etree
from PIL import Image
import json, re, html as esc, shutil

R=Path(__file__).resolve().parent; SITE=R.parent; SRC=R/'source/final14'
WORK=SITE.parent
KIZ=WORK/'kiz_package/PREP_KIZ_GEO_2026-10-20'
home=html.fromstring((SITE/'index.html').read_text())
inventory=json.loads((R/'page-inventory.json').read_text())
groups={'Услуги и категории','Статьи и требования маркетплейсов','Кейсы','Основные страницы'}
routes={x['path'] for x in inventory if x.get('group') in groups}
assert len(routes)==45
names={x['path']:x['title'].split(' | ')[0] for x in inventory}
newroutes=sorted(['/cases/agregatsiya-kiz-naborov-wms/','/cases/avtohimiya-2393-nabora-za-2-dnya/','/cases/avtomatizirovannaya-upakovka-kosmetiki/','/cases/kantselyarskie-nabory-6000-za-5-dney/','/cases/kosmetika-8400-za-2-dnya/','/cases/opolaskivateli-3186-za-2-dnya/','/cases/stroitelnaya-himiya-5180-za-3-dnya/','/cases/','/online/','/privacy-policy/','/tarify/','/blog/','/upakovka-bytovoy-khimii/','/agregatsiya-kiz-naborov/'])
assert len(newroutes)==14, newroutes
provenance=[]

def label(e): return ' '.join(' '.join(e.itertext()).split())
def frag(s): return html.fragment_fromstring(s,create_parent='div')
def put(e,s):
    for x in html.fragments_fromstring(s):
        if isinstance(x,str): e.text=(e.text or '')+x
        else: e.append(x)
def image_asset(source,name):
    out=SITE/'assets'/name
    if out.exists() and out.stat().st_size>0:return name
    im=Image.open(source).convert('RGB');im.thumbnail((1600,1600))
    im.save(out,'WEBP',quality=87,method=6)
    return name
for p in (KIZ/'photos/aggregation').glob('*.jpg'): image_asset(p,p.stem+'.webp')
for p in (WORK/'rawphotos').glob('autoline-*.png'): image_asset(p,p.stem+'.webp')
for p in (WORK/'rawphotos').glob('mouthwash-*.png'): image_asset(p,p.stem+'.webp')
for key in ['cosmetic','stationery']:
    for p in (WORK/'rawphotos').glob(key+'-*.png'):image_asset(p,key+'-'+p.name.split('-')[1]+'.webp')

def photo(name,alt,caption=None,eager=False):
    w,h=Image.open(SITE/'assets'/name).size
    fig=etree.Element('figure',{'class':'restore-photo'})
    etree.SubElement(fig,'img',src='/assets/'+name,alt=alt,width=str(w),height=str(h),loading='eager' if eager else 'lazy',decoding='async',style=f'aspect-ratio:{w}/{h}')
    if caption:etree.SubElement(fig,'figcaption').text=caption
    return fig
def setimage(im,name,eager=False):
    w,h=Image.open(SITE/'assets'/name).size
    for a in ['srcset','data-src','data-srcset','style']: im.attrib.pop(a,None)
    im.set('src','/assets/'+name);im.set('width',str(w));im.set('height',str(h));im.set('loading','eager' if eager else 'lazy');im.set('decoding','async');im.set('style',f'aspect-ratio:{w}/{h};height:auto')
def localize(block,current='/'):
    for el in block.xpath('.//*[@href or @src]'):
        if el.tag=='link' and el.get('rel')=='canonical':continue
        for attr in ['href','src']:
            val=el.get(attr)
            if not val:continue
            original=el.get('data-original-href') if attr=='href' else None
            candidate=original or val
            u=urlsplit(candidate)
            if u.scheme in ['tel','mailto']:continue
            if u.scheme and u.netloc not in ['prep-center.ru','www.prep-center.ru']:
                if el.tag=='a':el.set('target','_blank');el.set('rel','noopener')
                continue
            path=u.path
            if not path.startswith('/'):
                path=urlsplit(urljoin('https://prep-center.ru'+current,path)).path
            anchor=u.fragment
            if attr=='src':el.set(attr,path);continue
            if path=='/' and anchor in ['modal','calc','calculator']:el.set(attr,'#contact');continue
            if candidate in ['#modal','#calc']:el.set(attr,'#contact');continue
            if path=='/' and anchor in ['tariffs','tarify']:path='/tarify/';anchor='tariffs'
            if path in routes:
                el.set(attr,path+('#'+anchor if anchor else ''));continue
            if path.startswith('/assets/') or candidate.startswith('#'):
                el.set(attr,candidate if candidate.startswith('#') else path);continue
            if path.startswith(('/upload/','/local/')):continue
            # Keep the original target as evidence, but only expose functional contacts.
            el.set('data-original-href',candidate);el.set(attr,'#contact')
    for el in block.xpath('.//*[@onclick or @data-modal]'):
        el.attrib.pop('onclick',None);el.attrib.pop('data-modal',None)
    for el in list(block.xpath('.//form')):el.getparent().remove(el)

def related(block,targets):
    sec=etree.SubElement(block,'section',{'class':'restore-related','id':'final-recovery-related'})
    etree.SubElement(sec,'h2').text='Услуги и материалы по теме'
    grid=etree.SubElement(sec,'div',{'class':'restore-card-grid'})
    for p in dict.fromkeys(targets):
        etree.SubElement(grid,'a',href=p).text=names.get(p,p)
    return sec
def card(grid,path,title,description,image=None):
    a=etree.SubElement(grid,'a',href=path,attrib={'class':'restore-card'})
    if image:
        w,h=Image.open(SITE/'assets'/image).size
        etree.SubElement(a,'img',src='/assets/'+image,alt='',width=str(w),height=str(h),loading='lazy',decoding='async')
    etree.SubElement(a,'h3').text=title;etree.SubElement(a,'p').text=description
    return a

# Edit navigation at its canonical source and propagate the two common components.
for a in home.xpath('//header//a|//*[@id="contact"]//a'):
    t=label(a)
    mapping={'Тарифы':'/tarify/','Кейсы':'/cases/','Статьи':'/blog/','Преп-Центр в интернете':'/online/','Политика конфиденциальности':'/privacy-policy/','Политика обработки персональных данных':'/privacy-policy/'}
    if t in mapping:a.set('href',mapping[t]);a.set('data-original-href',mapping[t])
for el in home.xpath('//*[@id="restored-catalogs"]'):el.getparent().remove(el)
footer_nav=home.xpath('//*[@id="contact"]//nav')[0]
for p,t in [('/online/','Преп-Центр в интернете'),('/privacy-policy/','Политика обработки персональных данных')]:
    if not footer_nav.xpath('./a[@data-original-href=$p]',p=p):etree.SubElement(footer_nav,'a',href=p,**{'data-original-href':p}).text=t
localize(home)
header=deepcopy(home.xpath('//header')[0]);contact=deepcopy(home.xpath('//*[@id="contact"]')[0])

def shell(route,content,title,desc,css=(),kind='Article',published=None,modified=None,hero='warehouse-aisle.webp',source=''):
    localize(content,route)
    head=deepcopy(home.xpath('//head')[0]);head.xpath('./title')[0].text=title
    head.xpath('./meta[@name="description"]')[0].set('content',desc)
    head.xpath('./link[@rel="canonical"]')[0].set('href','https://prep-center.ru'+route)
    for link in head.xpath('./link[@rel="stylesheet"]'):
        link.set('href',urlsplit(urljoin('https://prep-center.ru/',link.get('href'))).path)
    for link in head.xpath('./link[@rel="preload"]'):
        if link.get('as')=='image':link.set('href','/assets/'+hero)
        else:link.set('href',urlsplit(urljoin('https://prep-center.ru/',link.get('href'))).path)
    for file in [*css,'final-recovery.css']:
        if not head.xpath('./link[@href=$h]',h='/assets/'+file):etree.SubElement(head,'link',rel='stylesheet',href='/assets/'+file)
    for prop,val in [('og:title',title),('og:description',desc),('og:url','https://prep-center.ru'+route),('og:type','article' if kind=='Article' else 'website'),('og:image','https://prep-center.ru/assets/'+hero)]:
        old=head.xpath('./meta[@property=$p]',p=prop)
        if old:old[0].set('content',val)
        else:etree.SubElement(head,'meta',property=prop,content=val)
    doc=etree.Element('html',lang='ru');doc.append(head);b=etree.SubElement(doc,'body');b.append(deepcopy(header));m=etree.SubElement(b,'main');m.append(content);m.append(deepcopy(contact))
    entity={'@context':'https://schema.org','@type':kind,'@id':'https://prep-center.ru'+route+'#content','url':'https://prep-center.ru'+route,'name':label(content.xpath('.//h1')[0]),'inLanguage':'ru-RU'}
    if published:entity['datePublished']=published
    if modified:entity['dateModified']=modified
    if kind=='Article':entity.update(headline=entity['name'],author={'@id':'https://prep-center.ru/#organization'},publisher={'@id':'https://prep-center.ru/#organization'},image=['https://prep-center.ru'+i.get('src') for i in content.xpath('.//img') if i.get('src','').startswith('/assets/')])
    elif kind=='Service':entity.update(provider={'@id':'https://prep-center.ru/#organization'},areaServed='Москва и Московская область')
    crumbs=[{'@type':'ListItem','position':1,'name':'Главная','item':'https://prep-center.ru/'}]
    if route.startswith('/cases/'):crumbs.append({'@type':'ListItem','position':2,'name':'Кейсы','item':'https://prep-center.ru/cases/'})
    if route!='/cases/':crumbs.append({'@type':'ListItem','position':len(crumbs)+1,'name':entity['name'],'item':'https://prep-center.ru'+route})
    nodes=[entity,{'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':crumbs}]
    faqs=[{'@type':'Question','name':label(x.xpath('./summary')[0]),'acceptedAnswer':{'@type':'Answer','text':' '.join(label(z) for z in x if z.tag!='summary')}} for x in content.xpath('.//details[summary]')]
    if faqs:nodes.append({'@context':'https://schema.org','@type':'FAQPage','mainEntity':faqs})
    for n in nodes:etree.SubElement(b,'script',type='application/ld+json').text=json.dumps(n,ensure_ascii=False)
    out=SITE/route.strip('/')/'index.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html'))
    provenance.append({'path':route,'source':source,'published':published,'updated':modified,'images':len(content.xpath('.//img')),'faq':len(faqs),'characters':len(label(content)),'title':title})
    return doc

CSS='''/* Recovery additions; original component styles remain in their own files. */
.restore-page{max-width:1180px;margin:auto;padding:36px 24px 70px;color:#172333;font:17px/1.7 Tilda,sans-serif}.restore-page h1{font-size:clamp(34px,5vw,58px);line-height:1.15;margin:24px 0}.restore-page h2{font:700 31px/1.25 Tilda,sans-serif;margin:42px 0 20px}.restore-page h3{font:600 23px/1.35 Tilda,sans-serif;margin:24px 0 12px}.restore-page p{margin:0 0 18px}.restore-page ul,.restore-page ol{padding-left:1.3em;list-style:revert}.restore-page li{margin:.4em 0}.restore-page a{color:#086593;text-decoration:underline;text-underline-offset:3px}.restore-date{color:#687482;font-size:14px;margin:15px 0!important}.restore-photo{margin:30px 0;min-width:0}.restore-photo img{width:100%;height:auto;max-height:650px;object-fit:contain;border-radius:16px;background:#f6f8fa}.restore-photo figcaption{font-size:14px;line-height:1.5;color:#617080;margin-top:10px}.restore-card-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.restore-card{display:block!important;border:1px solid #dfe6ec;border-radius:20px;padding:22px;background:#fff;color:#172333!important;text-decoration:none!important;min-width:0}.restore-card img{width:100%;height:200px;object-fit:contain;border-radius:12px;margin:0 0 16px}.restore-card h3{font:600 23px/1.3 Tilda,sans-serif;margin:0 0 12px}.restore-card p{font:16px/1.6 Tilda,sans-serif;margin:0}.restore-card:hover{border-color:#ff9800}.restore-related{margin:45px 0 20px;padding:25px;background:#f4f8fb;border-radius:20px}.restore-related h2{font:700 28px/1.3 Tilda,sans-serif!important;margin:0 0 20px!important}.restore-related .restore-card-grid>a{padding:16px;border:1px solid #dce4eb;border-radius:12px;background:white;color:#096290;font:16px/1.5 Tilda,sans-serif}.restore-page details{border:1px solid #dce4eb;border-radius:14px;margin:12px 0;padding:18px}.restore-page summary{font-weight:600;cursor:pointer}.restore-page details p{margin:14px 0 0}.restore-table-wrap{width:100%;overflow:auto}.restore-page table{width:100%;border-collapse:collapse;font-size:15px;table-layout:fixed;margin:20px 0}.restore-page th{background:#173a61;color:#fff;text-align:left}.restore-page th,.restore-page td{border:1px solid #dce4eb;padding:13px;vertical-align:top;overflow-wrap:anywhere}.tariff-table th:nth-child(1){width:27%}.tariff-table th:nth-child(2){width:13%}.tariff-table th:nth-child(3){width:15%}.tariff-table th:nth-child(4){width:45%}.restore-page input[type=search]{display:block;width:100%;padding:17px;border:1px solid #bac8d2;border-radius:12px;font:17px Tilda,sans-serif}.restore-page [hidden]{display:none!important}.restore-page .container{max-width:none;width:auto;padding:0}.restore-page [class*=__hero]>*{min-width:0}.restore-page img{max-width:100%;height:auto}.restored-original li{margin:.4em 0}.restored-original ul,.restored-original ol{padding-left:1.4em;list-style:revert}.restored-original [class*=__hero]>*,.restored-original [class*=__split]>*{min-width:0}.restored-original img{max-width:100%;height:auto!important}.restored-original [class*=__media] img,.restored-original [class*=__photo] img{width:100%;max-height:650px;object-fit:contain}.restored-original h3{font-family:Tilda,sans-serif}.restore-page .online-shell{width:100%}.restore-page .online-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.restore-page .online-page{font-family:Tilda,sans-serif}.restore-page .online-hero h1{font-family:Tilda,sans-serif}.restore-page .online-page h2{font-family:Tilda,sans-serif}.restore-page .online-page h3{font-family:Tilda,sans-serif}.restore-page .online-page a{overflow-wrap:anywhere}.restore-page blockquote{border-left:4px solid #ff9800;padding-left:20px;margin:25px 0}
@media(max-width:700px){.restore-page{padding:25px 18px 45px;font-size:16px}.restore-page h1{font-size:34px;overflow-wrap:anywhere}.restore-page h2{font-size:27px}.restore-card-grid,.restore-page .online-grid{grid-template-columns:1fr}.restore-photo img{max-height:500px}.restore-related{padding:18px}.restore-page table{font-size:12px}.restore-page td,.restore-page th{padding:8px}.tariff-table th:nth-child(1){width:29%}.tariff-table th:nth-child(2){width:17%}.tariff-table th:nth-child(3){width:18%}.tariff-table th:nth-child(4){width:36%}.restored-original h1{font-size:34px!important;overflow-wrap:anywhere}.restored-original [class*=__button]{white-space:normal}.restore-page .online-shell{width:100%}}
'''
(SITE/'assets/final-recovery.css').write_text(CSS)

# Retain all substantive sections of the five complete case snapshots.
casefiles=sorted(SRC.glob('0*__cases-*.html'))
maps={
'kantselyarskie-nabory-6000-za-5-dney':['stationery-10.webp','stationery-03.webp','stationery-01.webp','stationery-02.webp','stationery-04.webp','stationery-07.webp','stationery-09.webp'],
'kosmetika-8400-za-2-dnya':['cosmetic-01.webp','cosmetic-02.webp','cosmetic-03.webp','cosmetic-05.webp','cosmetic-06.webp','cosmetic-07.webp','cosmetic-08.webp'],
'opolaskivateli-3186-za-2-dnya':['mouthwash-06.webp','mouthwash-01.webp','mouthwash-02.webp','mouthwash-04.webp','mouthwash-03.webp','mouthwash-05.webp']}
case_rel={
'avtohimiya-2393-nabora-za-2-dnya':['/fulfillment-avtohimiya/','/komplektatsiya-naborov/','/termousadka-vpp/'],
'kantselyarskie-nabory-6000-za-5-dney':['/komplektatsiya-naborov/','/srochnaya-obrabotka-partiy/'],
'kosmetika-8400-za-2-dnya':['/fulfillment-kosmetika/','/chestnyy-znak/','/cases/avtomatizirovannaya-upakovka-kosmetiki/'],
'opolaskivateli-3186-za-2-dnya':['/fulfillment-zhidkih-tovarov/','/chestnyy-znak/','/termousadka-vpp/'],
'stroitelnaya-himiya-5180-za-3-dnya':['/fulfillment-stroitelnaya-himiya/','/termousadka-vpp/','/srochnaya-obrabotka-partiy/']}
for f in casefiles:
    slug=f.stem.split('__cases-',1)[1];route='/cases/'+slug+'/'
    source=html.fromstring(f.read_text());a=deepcopy(source.xpath('//article')[0]);a.set('class',a.get('class','')+' restored-original')
    css='\n'.join(x.text or '' for x in source.xpath('//main/style'));(SITE/'assets'/(slug+'.css')).write_text(css)
    ims=a.xpath('.//img')
    for i,im in enumerate(ims):setimage(im,maps[slug][i],i==0)
    # Where a specific original photo is unavailable, label the existing real photo literally.
    if False and slug=='kosmetika-8400-za-2-dnya':
        for i,alt in [(1,'Партия косметики на складе Преп-Центра'),(2,'Косметическая продукция при подготовке к поставке'),(5,'Косметическая продукция после защитной упаковки')]:
            ims[i].set('alt',alt)
            for cap in ims[i].getparent().xpath('./figcaption'):cap.text=alt+'; иллюстрация складской обработки'
    if False and slug=='kantselyarskie-nabory-6000-za-5-dney':
        alts=['Готовый канцелярский набор','Компоненты товарных наборов на складе','Складская обработка наборов','Комплектация наборов в Преп-Центре','Подготовка комплектующих для наборов','Сборка товарного набора','Пример готового канцелярского набора']
        for im,alt in zip(ims,alts):
            im.set('alt',alt)
            for cap in im.getparent().xpath('./figcaption'):cap.text=alt
    if not ims:
        sec=a.xpath('.//*[contains(@class,"__hero")]')[0]
        sec.append(photo('bubble-packed-set.webp' if slug.startswith('avto') else 'about-04-liniya-termousadki.webp','Упаковка товара в Преп-Центре','Реальный складской процесс Преп-Центра; иллюстрация услуги'))
    related(a[0],['/cases/',*case_rel[slug],'/tarify/'])
    published=None
    for sc in source.xpath('//script[@type="application/ld+json"]'):
        try:
            d=json.loads(sc.text);nodes=d.get('@graph',[d])
            for n in nodes:
                if n.get('datePublished'):published=n['datePublished'][:10]
        except (ValueError,TypeError):pass
    date=etree.Element('p',{'class':'restore-date'});date.text=('Опубликовано: '+published+' · ' if published else '')+'Восстановлено: 4 ноября 2026';a.xpath('.//h1')[0].addnext(date)
    shell(route,a,source.xpath('//title/text()')[0],source.xpath('//meta[@name="description"]/@content')[0],[slug+'.css'],published=published,hero=(ims[0].get('src').split('/')[-1] if ims else 'bubble-packed-set.webp'),source=f.name+'; поздний индекс проверен 04.11.2026')

# Preserve the policy verbatim, without inventing new legal terms.
source=html.fromstring((SRC/'033__privacy-policy.html').read_text());a=etree.Element('article',{'class':'restore-page'});box=deepcopy(source.xpath('//main/div')[0]);a.append(box)
shell('/privacy-policy/',a,source.xpath('//title/text()')[0],'Политика Преп-Центра в отношении обработки персональных данных.',kind='WebPage',source='Полный HTML 22.08.2026; текст сохранен без редакционных изменений')

# Complete late-index service copy is retained separately as evidence.
def markdown(text):
    # Use the project's established small Markdown parser, without running its build.
    globals()['set_fragment']=lambda e,s: put(e,s)
    code=(R/'build_ten.py').read_text();ns={'etree':etree,'re':re,'esc':esc,'set_fragment':lambda e,s:put(e,s)}
    exec(code[code.index('def inline'):code.index('def picture')],ns)
    return ns['parse'](text)
def generic(route,title,lead,date=None):
    a=etree.Element('article',{'class':'restore-page'});nav=etree.SubElement(a,'nav',{'aria-label':'Хлебные крошки'});etree.SubElement(nav,'a',href='/').text='Главная'
    if route.startswith('/cases/'):etree.SubElement(nav,'a',href='/cases/').text=' / Кейсы'
    etree.SubElement(a,'h1').text=title
    if date:etree.SubElement(a,'p',{'class':'restore-date'}).text=date
    if lead:etree.SubElement(a,'p').text=lead
    return a
def faq(a,pairs):
    etree.SubElement(a,'h2').text='Частые вопросы'
    for q,ans in pairs:
        d=etree.SubElement(a,'details');etree.SubElement(d,'summary').text=q;etree.SubElement(d,'p').text=ans
def section(a,title,text=None):
    s=etree.SubElement(a,'section');etree.SubElement(s,'h2').text=title
    if text:etree.SubElement(s,'p').text=text
    return s
def mdappend(a,text):
    for e in markdown(text):a.append(e)

route='/agregatsiya-kiz-naborov/'
a=generic(route,'Агрегация КИЗ при сборке маркированных наборов для маркетплейсов','Преп-Центр собирает маркированные наборы, связывает коды вложений с кодом набора в WMS и передает клиенту файл соответствий.','Опубликовано: 20 октября 2026 · Обновлено: 21 октября 2026')
text=(SRC/'web1.txt').read_text();chunk=next(x for x in text.split('--------------------------------------------------------------------------------') if '(https://prep-center.ru/agregatsiya-kiz-naborov/)' in x)
body=chunk[chunk.index('Принимаем отдельные'):];body=body.split('## Частые вопросы')[0]
body=re.sub(r'^Image:.*$','',body,flags=re.M)
body=re.sub(r'^Название услуги.*$|^---.*$','',body,flags=re.M)
body=body.replace('  * ','- ')
body=re.sub(r'^\s*(\d+)\. ### (.+)$',r'### \1. \2',body,flags=re.M)
mdappend(a,body)
# Restore the semantics of the original comparison table explicitly.
for p in list(a.xpath('./p')):
    if 'Объект и код' in label(p) or label(p).startswith(('Набор, КИН','Косметика и бытовая химия','Комплект, КИК','Легкая промышленность','Транспортная упаковка, SSCC')):p.getparent().remove(p)
table=html.fromstring('<div class="restore-table-wrap"><table><thead><tr><th>Объект и код</th><th>Что означает</th></tr></thead><tbody><tr><td>Набор, КИН. Косметика и бытовая химия</td><td>Товары в общей потребительской упаковке. Состав связывают с кодом набора; предусмотрена возможность расформирования.</td></tr><tr><td>Комплект, КИК. Легкая промышленность</td><td>Определенный производителем единый товар. При передаче права собственности его не разукомплектовывают. Товары внутри такого комплекта отдельно не маркируются.</td></tr><tr><td>Транспортная упаковка, SSCC</td><td>Объединение маркированных единиц в транспортный короб или паллету либо упаковок в логистическую единицу следующего уровня.</td></tr></tbody></table></div>')
heading=next(x for x in a.xpath('./h2') if label(x)=='Набор, комплект и транспортная упаковка');heading.addnext(table)
a.insert(4,photo('agg-06-finished-set.webp','Готовый маркированный набор в общей упаковке','Реальный образец после сборки и маркировки.',True))
heading=next(x for x in a.xpath('./h2') if 'Что видит сотрудник' in label(x));heading.addnext(photo('agg-04-wms-counter.webp','Рабочее окно агрегации КИЗ в МПФИТ','Счетчик 0/2 относится к 2 вложениям одного набора.'))
faq(a,[('Кто выпускает коды готовых наборов?','Клиент выпускает коды и загружает их в соответствующий товар WMS. Порядок подготовки и статусы согласовываем до передачи партии.'),('Нужно заранее заполнять Excel с кодами каждого вложения?','Связь формируется в WMS по результатам сканирования каждой единицы при сборке. Формат дальнейшей выгрузки согласовываем заранее.'),('Когда печатается общая этикетка?','После сканирования всех вложений, предусмотренных составом конкретного набора.'),('Кто выполняет оформление в «Честном знаке»?','Клиент скачивает файл соответствий и продолжает оформление в системе маркировки. Действия зависят от товарной группы и статусов кодов.'),('Агрегация и дублирование КИЗ стоят одинаково?','Это разные операции. Цена 7 ₽ за дублирование кода одной единицы не определяет стоимость агрегации; ее рассчитываем по составу партии.'),('Можно совместить сборку с упаковкой и FBO?','Да, состав операций, общую упаковку и требования к дальнейшей поставке согласовываем до запуска.')])
related(a,['/cases/agregatsiya-kiz-naborov-wms/','/komplektatsiya-naborov/','/chestnyy-znak/','/wms-mpfit-dlya-fulfillmenta/','/tarify/'])
shell(route,a,'Агрегация КИЗ наборов для маркетплейсов через WMS | Преп-Центр','Сборка маркированных наборов, сканирование вложений, связь кодов в WMS МПФИТ и файл соответствий для клиента.',kind='Service',published='2026-10-20',modified='2026-10-21',hero='agg-06-finished-set.webp',source='Поздняя индексная редакция 21.10.2026; исходный пакет 20.10.2026')

route='/cases/agregatsiya-kiz-naborov-wms/'
a=generic(route,'Агрегация КИЗ при сборке набора через WMS МПФИТ','Преп-Центр связывает КИЗ вложений с кодом набора в WMS МПФИТ и передает клиенту файл соответствий.','Опубликовано: 20 октября 2026 · Обновлено: 21 октября 2026')
raw=(KIZ/'02_CASE_AGGREGATION.md').read_text();body=raw.split('## 2. Полный публикуемый текст',1)[1].split('## 3. Шесть изображений',1)[0]
body=re.sub(r'\[\[AGENT: H2\]\]','',body)
captions={
'agg-01-set-with-components.jpg':('Набор из 2 маркированных товаров и готовая упаковка','До начала сканирования: 2 отдельных товара для одного набора'),
'agg-04-wms-counter.jpg':('Окно агрегации КИЗ в WMS МПФИТ со счетчиком 0/2','Система показывает ожидаемое число сканирований'),
'agg-02-scan-component-a.jpg':('Считывание КИЗ первого товара сканером','Первый код привязывается к заданию на сборку'),
'agg-03-scan-component-b.jpg':('Сканирование КИЗ второго вложения','Считываем код каждой фактической единицы'),
'agg-05-label-printing.jpg':('Принтер с этикеткой маркированного набора','Общая этикетка печатается после сканирования вложений'),
'agg-06-finished-set.jpg':('Готовый набор с внешней этикеткой','Образец после комплектации и упаковки')}
for part in re.split(r'(\[\[AGENT: IMAGE [^\]]+\]\])',body):
    m=re.match(r'\[\[AGENT: IMAGE ([^\]]+)\]\]',part)
    if m:
        name=m[1];alt,cap=captions[name];a.append(photo(name.replace('.jpg','.webp'),alt,cap))
    else:mdappend(a,part)
section(a,'Условия применения','Слово «набор» здесь описывает складскую сборку из нескольких маркированных единиц. Юридический тип объекта и порядок оформления проверяют для конкретной категории до начала работы. Отличия набора, комплекта и транспортной упаковки разобраны на странице услуги.')
related(a,['/agregatsiya-kiz-naborov/','/komplektatsiya-naborov/','/chestnyy-znak/','/wms-mpfit-dlya-fulfillmenta/','/cases/'])
shell(route,a,'Агрегация КИЗ набора через WMS: технологический кейс | Преп-Центр','Реальный складской процесс: сканирование каждого вложения, связь кодов набора в МПФИТ, печать этикетки и файл соответствий.',published='2026-10-20',modified='2026-10-21',hero='agg-06-finished-set.webp',source='Полный исходный MD 20.10; фотографии из пакета; уточнения опубликованной редакции 21.10')

route='/cases/avtomatizirovannaya-upakovka-kosmetiki/'
a=generic(route,'Автоматизированная упаковка косметики: ВПП, термоусадка и дублирование КИЗ','Преп-Центр последовательно упаковывает косметику в ВПП и термоусадку, сохраняя доступ к КИЗ на внешнем слое.','Опубликовано: 21 октября 2026')
a.append(photo('autoline-01.webp','Линия упаковки косметики в Преп-Центре','Связанная линия для двух последовательных слоев защитной упаковки.',True))
section(a,'Задача клиента','Для крупной партии косметики нужно совместить защитную упаковку и доступность маркировки. В показанной линии товар сначала оборачивается в воздушно-пузырчатую пленку, затем поступает на термоусадку. Автоматизация сокращает повторяющиеся ручные операции.')
section(a,'Возможности линии','До 20 000 единиц за смену при среднем габаритном объеме товара до 1 литра по внешним размерам. Производительность зависит от размеров и особенностей продукции. Это заявленная возможность оборудования, а не измеренный объем данного заказа.')
section(a,'1. Сканирование заводского КИЗ','На входе сотрудник сканирует заводской КИЗ конкретной единицы. Этот же код используют для печати дубликата на выходе, без ручного переноса длинной строки символов.');a.append(photo('autoline-02.webp','Сканирование заводского кода перед упаковкой','На входе фиксируем код конкретной единицы товара.'))
section(a,'2. Первый слой: воздушно-пузырчатая пленка','ВПП создает амортизирующую прослойку вокруг товара. После формирования первого слоя единица переходит к следующей операции на той же линии.');a.append(photo('autoline-03.webp','Формирование первого защитного слоя ВПП','Товар проходит первый этап последовательной упаковки.'));a.append(photo('autoline-04.webp','Косметика в ВПП на транспортере','После первого слоя товар перемещается к термоусадке.'))
section(a,'3. Второй слой: термоусадочная пленка','Термоусадочная пленка образует внешний слой и удерживает защитную упаковку вокруг товара. В этом сценарии последовательность: ВПП, затем термоусадка. Для других товаров технологическую схему согласовываем отдельно.');a.append(photo('autoline-05.webp','Товар после двух последовательных операций упаковки','Внешний слой фиксирует защитную упаковку вокруг продукции.'))
section(a,'4. Дубликат того же кода снаружи','После упаковки печатаем и наносим дубликат заводского КИЗ, который отсканировали на входе. Внешняя этикетка относится к той же единице. Код доступен для сканирования при приемке и учете без вскрытия защитной упаковки.');a.append(photo('autoline-07.webp','Косметика с доступной снаружи маркировкой','Готовый товар с защитной упаковкой и внешним дубликатом КИЗ.'))
section(a,'Что получает клиент','Товар с 2 защитными слоями и доступной снаружи маркировкой. Упаковка и дублирование кода выполняются в рамках обработки одной партии. Цена зависит от товара, размеров, объема, материалов и состава операций.')
section(a,'Оборудование участка','Помимо связанной линии есть отдельный термоусадочный станок для самостоятельной операции. Подходящий способ и настройки подтверждаем на образце.');a.append(photo('autoline-08.webp','Работа оператора на участке упаковки','Складской участок и оборудование Преп-Центра.'))
faq(a,[('В каком порядке формируются 2 слоя?','В показанном кейсе косметики сначала ВПП, затем термоусадка. Последовательность других процессов зависит от товара и технологической схемы.'),('Снаружи размещается новый КИЗ?','На внешнюю упаковку переносится дубликат заводского кода той же единицы, считанного перед упаковкой.'),('Это агрегация набора?','Здесь обрабатывают отдельную единицу и дублируют ее код. Агрегация связывает несколько вложений с кодом общей упаковки и описана отдельно.'),('20 000 единиц означает объем выполненного заказа?','Нет. Это заявленная производительность при подходящем товаре со средним габаритным объемом до 1 литра. Объем этой партии и длительность заказа в источнике не раскрыты.'),('Можно заказать только термоусадку?','Да, на участке есть отдельный термоусадочный станок. Технологию и стоимость согласовываем по товару.'),('Что прислать для расчета?','Фото товара, внешние размеры, объем партии и перечень операций. Менеджер подтвердит подходящую упаковку, сроки и стоимость.')])
etree.SubElement(a,'p').text='Источник: рабочий документ Преп-Центра. Данные клиента скрыты, рисунок кодов изменен для публикации.'
related(a,['/termousadka-vpp/','/fulfillment-kosmetika/','/fulfillment-zhidkih-tovarov/','/chestnyy-znak/','/srochnaya-obrabotka-partiy/','/cases/'])
shell(route,a,'Автоматизированная упаковка косметики: технологический кейс | Преп-Центр','Реальная линия: ВПП, термоусадка и внешний дубликат заводского КИЗ. Семь фотографий процесса и условия применения.',published='2026-10-21',hero='autoline-01.webp',source='Полный DOCX автоматической линии; 7 исходных кадров из 8 встроенных; ТЗ 21.10.2026')

# Price catalog: 129 described services + four FBY routes + picking added 20 October.
cat=json.loads((SRC/'tariffs-source.json').read_text());cats=deepcopy(cat['itemListElement'])
for c in cats:
    for o in c['itemListElement']:
        item=o['itemOffered'];p=o.get('priceSpecification',{})
        updates={'Сборка монопаллета':600,'Паллетирование товара':400,'Подготовка короба 60×40×40 к отгрузке':150}
        if item['name'] in updates:p['price']=updates[item['name']];p.pop('minPrice',None)
pick={'@type':'Offer','priceSpecification':{'@type':'UnitPriceSpecification','price':10,'priceCurrency':'RUB','unitText':'1 шт.','valueAddedTaxIncluded':False},'itemOffered':{'@type':'Service','identifier':'PC-TAR-130','name':'Поштучный подбор товара','serviceType':'Приемка, проверка и сортировка','description':'Сборка товара отдельными единицами до или после выполнения ТЗ для распределения по разным коробам, поставкам или городам. При отгрузке целыми коробами услуга не требуется. Стоимость без НДС.'}}
next(c for c in cats if c['name']=='Приемка, проверка и сортировка')['itemListElement'].append(pick)
ym={'@type':'OfferCatalog','name':'Доставка на склады Яндекс Маркета','itemListElement':[]}
for place,address,pallet,nextp,boxes,boxprice,hours in [('Мытищи, транзитный склад','Московская область, Мытищи, Осташковское шоссе, 17А',5500,4000,10,550,'Приемка ежедневно с 12:00 до 20:00; далее груз следует на Софьино-1.'),('Софьино-1, стандартный склад','Московская область, Раменский г. о., логистический технопарк «Софьино», стр. 3/1',6000,5100,6,800,'Склад работает круглосуточно; для въезда нужен пропуск.')]:
    for mode,price,unit,details in [('паллетами',pallet,'1-й паллет до 350 кг',f'Первый паллет — {pallet} ₽, каждый последующий — {nextp} ₽.'),('коробами',boxes*boxprice,f'минимум {boxes} коробов',f'Минимум {boxes} коробов — {boxes*boxprice} ₽, каждый следующий — {boxprice} ₽.')]:
        ym['itemListElement'].append({'@type':'Offer','priceSpecification':{'@type':'UnitPriceSpecification','price':price,'priceCurrency':'RUB','unitText':unit,'valueAddedTaxIncluded':False},'itemOffered':{'@type':'Service','name':f'Доставка FBY: {place} — {mode}','serviceType':ym['name'],'description':f'Адрес: {address}. {hours} {details} Дата выезда согласовывается по созданной поставке и подтвержденному слоту. Тариф Преп-Центра, без НДС.'}})
cats.insert(-1,ym);assert sum(len(c['itemListElement']) for c in cats)==134
route='/tarify/';a=generic(route,'Тарифы на фулфилмент и подготовку товаров к маркетплейсам','Здесь собраны 134 тарифа Преп-Центра на приемку, сортировку, маркировку, упаковку, хранение, FBO/FBS и доставку.','Опубликовано: 27 августа 2026 · Обновлено: 20 октября 2026')
etree.SubElement(a,'p').text='Цены указаны без НДС. Итоговая стоимость зависит от объема, габаритов, материалов, состава операций и маршрута. Информация не является публичной офертой.'
lab=etree.SubElement(a,'label',{'for':'tariff-search'});lab.text='Поиск по названию услуги и описанию'
etree.SubElement(a,'input',type='search',id='tariff-search',placeholder='Например, паллетирование или доставка',**{'aria-describedby':'tariff-count'})
etree.SubElement(a,'p',id='tariff-count',**{'aria-live':'polite'}).text='Найдено 134 тарифа'
root=etree.SubElement(a,'div',id='tariffs')
for c in cats:
    sec=etree.SubElement(root,'section',{'class':'tariff-category'});etree.SubElement(sec,'h2').text=c['name'];etree.SubElement(sec,'p').text=str(len(c['itemListElement']))+' тарифов'
    wrap=etree.SubElement(sec,'div',{'class':'restore-table-wrap'});tab=etree.SubElement(wrap,'table',{'class':'tariff-table'});tr=etree.SubElement(etree.SubElement(tab,'thead'),'tr')
    for h in ['Название услуги','Цена','За что','Описание']:etree.SubElement(tr,'th',scope='col').text=h
    tbody=etree.SubElement(tab,'tbody')
    for o in c['itemListElement']:
        it=o['itemOffered'];p=o.get('priceSpecification',{});price=p.get('price',p.get('minPrice'));value=('от ' if 'minPrice' in p else '')+f'{price:,.0f}'.replace(',',' ')+' ₽' if price is not None else 'По договоренности'
        tr=etree.SubElement(tbody,'tr',{'class':'tariff-row'});tr.set('data-search',(it['name']+' '+it['description']).lower())
        for t in [it['name'],value,p.get('unitText','по согласованию'),it['description']]:etree.SubElement(tr,'td').text=t
related(a,['/fulfillment-fbo/','/fulfillment-fbs/','/fby-yandex-market/','/fbl-letual/','/agregatsiya-kiz-naborov/','/contacts/'])
doc=shell(route,a,'Тарифы на фулфилмент для маркетплейсов | Преп-Центр','134 тарифа: приемка, сортировка, маркировка, упаковка, хранение и доставка. Цены с изменениями 20 октября 2026.',kind='CollectionPage',published='2026-08-27',modified='2026-10-20',source='Полная схема каталога 129 услуг; архив прайсов 20.10.2026; 4 осенних FBY-тарифа из позднего индекса')
catalog={'@context':'https://schema.org','@type':'OfferCatalog','@id':'https://prep-center.ru/tarify/#catalog','name':'Тарифы Преп-Центра','numberOfItems':134,'itemListElement':cats}
etree.SubElement(doc.xpath('//body')[0],'script',type='application/ld+json').text=json.dumps(catalog,ensure_ascii=False)
etree.SubElement(doc.xpath('//body')[0],'script',src='/assets/tariff-search.js',defer='defer')
(SITE/'tarify/index.html').write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html'))
(SRC/'tariffs-restored.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
(SITE/'assets/tariff-search.js').write_text("const input=document.getElementById('tariff-search');input.addEventListener('input',()=>{const q=input.value.trim().toLocaleLowerCase('ru');let count=0;document.querySelectorAll('.tariff-category').forEach(section=>{let n=0;section.querySelectorAll('.tariff-row').forEach(row=>{row.hidden=!row.dataset.search.includes(q);if(!row.hidden)n++});section.hidden=n===0;count+=n});document.getElementById('tariff-count').textContent='Найдено тарифов: '+count});")

# External profiles: complete original markup, plus the confirmed September article.
source=html.fromstring((SRC/'online-source.html').read_text());css='\n'.join(x.text or '' for x in source.xpath('//style'));(SITE/'assets/online-restored.css').write_text(css)
online=deepcopy(source.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," online-page ")]')[0]);a=etree.Element('article',{'class':'restore-page'});a.append(online)
for im in a.xpath('.//img'):
    number=unquote(urlsplit(im.get('src')).path).split('/')[-1][:2]
    setimage(im,'online-'+number+'.webp')
for l in a.xpath('.//a'):
    if l.get('href')=='https://yandex.ru/maps/-/CDTVNMlf':l.set('href','https://yandex.ru/maps/org/prep_tsentr/113144699853/')
media=next((x for x in a.xpath('.//section') if x.xpath('.//h2') and 'СМИ' in label(x.xpath('.//h2')[0])),None)
if media is not None:
    entry=html.fromstring('<div class="restore-related"><p>9 сентября 2026 · Рейтинг</p><h3><a href="https://www.klerk.ru/user/2721035/708274/" target="_blank" rel="noopener">Фулфилменты для маркетплейсов: 10 лучших компаний для селлеров на Ozon и Wildberries</a></h3><p>Сравнение операторов Москвы и Московской области по подготовке крупных партий, упаковке, маркировке и отгрузкам FBO/FBS.</p></div>');media.insert(1,entry)
related(a,['/about/','/contacts/','/cases/','/blog/'])
shell('/online/',a,'Преп-Центр в интернете: официальные профили, рейтинги и публикации','Официальные профили Преп-Центра, отзывы, рейтинги и материалы о работе компании.',['online-restored.css'],kind='CollectionPage',source='Полный исходный HTML внешних профилей; поздний индекс и подтвержденная ссылка Клерк 09.09.2026')

# The complete historical article is preserved, including all of its substantive sections.
source=html.fromstring((SRC/'011__upakovka-bytovoy-khimii.html').read_text());a=deepcopy(source.xpath('//main/article')[0]);a.set('class',a.get('class','')+' restored-original')
(SITE/'assets/upakovka-bytovoy-khimii.css').write_text('\n'.join(x.text or '' for x in source.xpath('//head/style')))
for i,im in enumerate(list(a.xpath('.//img'))):
    if 'Логотип клиента' in im.get('alt',''):
        par=im.getparent();par.remove(im);continue
    name=['household-hero.webp','about-04-liniya-termousadki.webp','pack-01.webp','pack-02.webp','pack-03.webp'][min(i,4)];setimage(im,name,i==0)
    im.set('alt','Упаковка и подготовка товаров в Преп-Центре')
    parent=im.getparent()
    if parent.tag=='a' and parent.get('href','').startswith('/upload/'):
        parent.set('href',im.get('src'));parent.attrib.pop('data-fslightbox',None);parent.set('target','_blank');parent.set('rel','noopener')
# Only three distinct packing photos are available; do not clone the last one into missing slots.
for gallery in a.xpath('.//div[@class="prep-article-gallery"]'):
    seen=set()
    for item in list(gallery):
        photos=item.xpath('.//img')
        if not photos:continue
        src=photos[0].get('src')
        if src in seen:
            gallery.remove(item);continue
        seen.add(src)
        item.set('class','prep-article-gallery__item')
        photos[0].attrib.pop('style',None)
for e in list(a.xpath('.//form')):e.getparent().remove(e)
for item in list(a.xpath('.//div[contains(concat(" ",@class," ")," prep-article-faq__item ")]')):
    question=item.xpath('./button')[0];answer=item.xpath('./div')[0]
    details=etree.Element('details',{'class':'restored-faq-item'});etree.SubElement(details,'summary').text=label(question).rstrip('+−– ')
    for child in list(answer):details.append(child)
    item.getparent().replace(item,details)
for link in a.xpath('.//a[contains(@class,"btn")]'):link.set('href','#contact')
related(a,['/fulfillment-bytovaya-himiya/','/termousadka-vpp/','/fulfillment-zhidkih-tovarov/','/blog/'])
shell('/upakovka-bytovoy-khimii/',a,'Упаковка бытовой химии | Преп-Центр','Материалы, защита и подготовка бытовой химии к хранению, перевозке и продаже.',['upakovka-bytovoy-khimii.css'],published='2026-08-22',hero='household-hero.webp',source='Полный HTML 22.08.2026; текст сверяется с августовским индексом; недоступные изображения заменены существующими фото упаковки, без логотипов клиентов')

# Build complete, current directories instead of publishing their obsolete August subset.
titles={p['path']:(p['title'],p['images']) for p in provenance}
for p in routes:
    f=SITE/p.strip('/')/'index.html'
    if f.exists():names[p]=label(html.fromstring(f.read_text()).xpath('//h1')[0])
case_descriptions={
'/cases/agregatsiya-kiz-naborov-wms/':('Сканирование вложений, сопоставление кодов в WMS и общая этикетка. Технологический кейс.','agg-06-finished-set.webp'),
'/cases/avtomatizirovannaya-upakovka-kosmetiki/':('Последовательная линия: ВПП, термоусадка и дубликат заводского КИЗ снаружи.','autoline-01.webp'),
'/cases/avtohimiya-2393-nabora-za-2-dnya/':('2 393 готовых подарочных набора из партии на 2 400 наборов за 2 рабочих дня.','bubble-packed-set.webp'),
'/cases/kantselyarskie-nabory-6000-za-5-dney/':('24 комплектующих в каждом наборе и более 144 000 отдельных единиц в обработке.','stationery-set.webp'),
'/cases/kosmetika-8400-za-2-dnya/':('14 SKU на 7 паллетах. После контроля подготовлено 8 357 единиц и 5 FBO-поставок.','cos-01.webp'),
'/cases/opolaskivateli-3186-za-2-dnya/':('Индивидуальная упаковка в ВПП и дубликат кода маркировки на внешнем слое.','mouthwash-06.webp'),
'/cases/stroitelnaya-himiya-5180-za-3-dnya/':('Термоусадка, ВПП и подготовка пригодной партии к продаже за 3 рабочих дня.','about-04-liniya-termousadki.webp')}
a=generic('/cases/','Кейсы Преп-Центра','Реальные проекты подготовки товаров к маркетплейсам и технологические примеры работы склада.')
grid=etree.SubElement(a,'div',{'class':'restore-card-grid'})
for p,(desc,img) in case_descriptions.items():card(grid,p,names[p],desc,img)
related(a,['/komplektatsiya-naborov/','/fulfillment-kosmetika/','/termousadka-vpp/','/agregatsiya-kiz-naborov/','/tarify/'])
shell('/cases/',a,'Кейсы Преп-Центра: упаковка, маркировка и подготовка поставок','Все 7 восстановленных кейсов Преп-Центра: косметика, автохимия, наборы, ополаскиватели, строительная химия, КИЗ и автоматическая линия.',kind='CollectionPage',source='Архив каталога 22.08; перечень осенних кейсов из поздней главной; все 7 восстановленных страниц')
a=generic('/blog/','Статьи о фулфилменте и упаковке','Практические материалы Преп-Центра об упаковке, складском учете и требованиях к подготовке поставок.')
grid=etree.SubElement(a,'div',{'class':'restore-card-grid'})
for p,desc,img in [('/wms-mpfit-dlya-fulfillmenta/','Как устроены остатки, складские операции, личный кабинет и КИЗ.','wms-01.webp'),('/upakovka-bytovoy-khimii/','Материалы и подготовка упаковки для бытовой химии.','household-hero.webp')]:card(grid,p,names[p],desc,img)
section(a,'Требования маркетплейсов','Инструкции восстановлены по исходным материалам сентября 2026. Перед поставкой сверяйте текущий регламент и параметры заявки в кабинете площадки.')
grid=etree.SubElement(a,'div',{'class':'restore-card-grid'})
for p in sorted(x for x in routes if x.startswith('/trebovaniya-')):card(grid,p,names[p],'Упаковка, маркировка и подготовка поставки.')
related(a,['/cases/','/online/','/tarify/','/contacts/'])
shell('/blog/',a,'Статьи об упаковке и фулфилменте | Преп-Центр','Складской учет, упаковка товаров, FBO, FBS и требования Ozon, Wildberries, Яндекс Маркета и ЛЭТУАЛЬ.',kind='CollectionPage',source='Августовский HTML каталога; дополнен всеми восстановленными статьями сентября и WMS')

# Activate previously stored original destinations, plus reciprocal topic links.
topic={
'/chestnyy-znak/':['/agregatsiya-kiz-naborov/','/cases/agregatsiya-kiz-naborov-wms/','/cases/avtomatizirovannaya-upakovka-kosmetiki/'],
'/komplektatsiya-naborov/':['/agregatsiya-kiz-naborov/','/cases/kantselyarskie-nabory-6000-za-5-dney/','/cases/avtohimiya-2393-nabora-za-2-dnya/'],
'/fulfillment-kosmetika/':['/cases/kosmetika-8400-za-2-dnya/','/cases/avtomatizirovannaya-upakovka-kosmetiki/'],
'/fulfillment-avtohimiya/':['/cases/avtohimiya-2393-nabora-za-2-dnya/'],
'/fulfillment-stroitelnaya-himiya/':['/cases/stroitelnaya-himiya-5180-za-3-dnya/'],
'/fulfillment-bytovaya-himiya/':['/upakovka-bytovoy-khimii/'],
'/fulfillment-zhidkih-tovarov/':['/cases/opolaskivateli-3186-za-2-dnya/','/cases/avtomatizirovannaya-upakovka-kosmetiki/'],
'/wms-mpfit-dlya-fulfillmenta/':['/agregatsiya-kiz-naborov/','/cases/agregatsiya-kiz-naborov-wms/'],
'/termousadka-vpp/':['/cases/avtomatizirovannaya-upakovka-kosmetiki/','/cases/stroitelnaya-himiya-5180-za-3-dnya/'],
'/srochnaya-obrabotka-partiy/':['/cases/avtomatizirovannaya-upakovka-kosmetiki/','/cases/'],
'/about/':['/cases/avtomatizirovannaya-upakovka-kosmetiki/','/online/']}
related_home=etree.Element('section',{'class':'recovery-guides','id':'restored-catalogs'});etree.SubElement(related_home,'h2').text='Кейсы, статьи и тарифы';grid=etree.SubElement(related_home,'div',{'class':'recovery-guides__grid'})
for p,t in [('/cases/','Все кейсы'),('/blog/','Статьи и инструкции'),('/tarify/','Все 134 тарифа'),('/online/','Преп-Центр в интернете')]:etree.SubElement(grid,'a',href=p).text=t
home.xpath('//*[@id="contact"]')[0].addprevious(related_home)
for p,(desc,img) in list(case_descriptions.items())[:2]:
    grid=home.xpath('//*[@id="restored-catalogs"]/div')[0];etree.SubElement(grid,'a',href=p).text=names[p]
for route in routes:
    f=SITE/route.strip('/')/'index.html'
    d=home if route=='/' else html.fromstring(f.read_text())
    localize(d,route)
    if route in topic:
        article=d.xpath('//main/article')[0]
        if not article.xpath('.//*[@id="final-recovery-related"]'):related(article[0] if len(article) and article[0].tag=='div' else article,topic[route])
        if not d.xpath('//link[@href="/assets/final-recovery.css"]'):etree.SubElement(d.xpath('//head')[0],'link',rel='stylesheet',href='/assets/final-recovery.css')
    # Remove obsolete generic source targets when the concrete restored target is known.
    for a in d.xpath('//a[@href="#contact"][@data-original-href]'):
        target=a.get('data-original-href');u=urlsplit(target)
        if u.path in routes and u.fragment not in ['calc','modal','calculator']:a.set('href',u.path+('#'+u.fragment if u.fragment else ''))
    d.xpath('//link[@rel="canonical"]')[0].set('href','https://prep-center.ru'+route)
    if route!='/':
        old=d.xpath('//header')[0];old.getparent().replace(old,deepcopy(header))
        old=d.xpath('//*[@id="contact"]')[0];old.getparent().replace(old,deepcopy(contact))
    f.write_text('<!doctype html>\n'+html.tostring(d,encoding='unicode',method='html'))

(SRC/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
for row in inventory:
    if row['path'] in newroutes:
        p=next(x for x in provenance if x['path']==row['path']);row['status']=f"Восстановлена; {p['images']} изображений; тематические и обратные ссылки";row['latest_capture']=p['source']
(R/'page-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
print(json.dumps(provenance,ensure_ascii=False,indent=2))
