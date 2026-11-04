from pathlib import Path
from lxml import html
from urllib.parse import urlsplit,unquote
import json,sys
SITE=Path(__file__).resolve().parent.parent
inv=json.loads((SITE/'restoration/page-inventory.json').read_text())
routes={x['path'] for x in inv if x.get('group') in {'Услуги и категории','Статьи и требования маркетплейсов','Кейсы','Основные страницы'}}
errors=[];graph={};img_count=0
for route in sorted(routes):
    file=SITE/route.strip('/')/'index.html';d=html.fromstring(file.read_text());graph[route]=set()
    if len(d.xpath('//h1'))!=1:errors.append((route,'H1',len(d.xpath('//h1'))))
    if len(d.xpath('//body/header'))!=1 or len(d.xpath('//*[@id="contact"]'))!=1:errors.append((route,'shared-components'))
    if d.xpath('//link[@rel="canonical"]/@href')!=['https://prep-center.ru'+route]:errors.append((route,'canonical'))
    if d.xpath('//meta[@name="robots"]/@content')!=['noindex,follow']:errors.append((route,'robots'))
    text=' '.join(d.xpath('//main')[0].itertext())
    for marker in ['[[AGENT:','[ИЗОБРАЖЕНИЕ']:
        if marker in text:errors.append((route,'raw marker',marker))
    for sc in d.xpath('//script[@type="application/ld+json"]'):
        try:json.loads(sc.text)
        except Exception as e:errors.append((route,'JSON',str(e)))
    for el in d.xpath('//*[@href or @src]'):
        for attr in ['href','src']:
            href=el.get(attr)
            if not href:continue
            u=urlsplit(href)
            if u.scheme or href.startswith('//'):continue
            target=SITE/unquote(u.path).lstrip('/') if u.path.startswith('/') else (file.parent/unquote(u.path) if u.path else file)
            if target.is_dir():target/='index.html'
            if not target.exists():errors.append((route,'missing',href));continue
            if target.name=='index.html':
                targetroute='/'+str(target.parent.relative_to(SITE)).strip('.')+'/'
                targetroute=targetroute.replace('//','/')
                if targetroute in routes:graph[route].add(targetroute)
            if u.fragment and target.suffix=='.html':
                if not html.fromstring(target.read_text()).xpath('//*[@id=$id]',id=u.fragment):errors.append((route,'anchor',href))
    img_count+=len(d.xpath('//main/article//img'))
seen={'/'}
while True:
    n=seen|set.union(*(graph[x] for x in seen))
    if n==seen:break
    seen=n
if seen!=routes:errors.append(('unreachable',sorted(routes-seen)))
price=html.fromstring((SITE/'tarify/index.html').read_text())
if len(price.xpath('//tr[@class="tariff-row"]'))!=134:errors.append(('tariff count',len(price.xpath('//tr[@class="tariff-row"]'))))
for name,value in [('Сборка монопаллета','600 ₽'),('Паллетирование товара','400 ₽'),('Подготовка короба 60×40×40 к отгрузке','150 ₽'),('Поштучный подбор товара','10 ₽')]:
    rows=price.xpath('//tr[@class="tariff-row"][td[1]=$name]',name=name)
    if len(rows)!=1 or rows[0].xpath('./td[2]/text()')!=[value]:errors.append(('price',name,value))
result={'pages':len(routes),'reachable':len(seen),'article_images':img_count,'errors':errors,'graph':{k:sorted(v) for k,v in graph.items()}}
(SITE/'restoration/source/final14/structural-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='graph'},ensure_ascii=False,indent=2))
sys.exit(bool(errors))
