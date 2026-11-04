from pathlib import Path
from lxml import html
import json
ROOT=Path(__file__).resolve().parent.parent
routes=[x['path'] for x in json.loads((ROOT/'restoration/page-inventory.json').read_text()) if x.get('group') in {'Услуги и категории','Статьи и требования маркетплейсов','Кейсы','Основные страницы'}]
reference=None
for route in routes:
 d=html.fromstring((ROOT/route.strip('/')/'index.html').read_text())
 header=d.xpath('//body/header');contact=d.xpath('//*[@id="contact"]')
 assert len(header)==len(contact)==1,route
 pair=tuple(html.tostring(x,with_tail=False) for x in [header[0],contact[0]])
 if reference is None:reference=pair
 assert pair==reference,('global mismatch',route)
 nav=d.xpath('//nav[contains(@class,"desktop-nav")]/ul')[0]
 mobile=d.xpath('//nav[@aria-label="Меню в сэндвиче"]/ul')[0]
 assert html.tostring(nav,with_tail=False)==html.tostring(mobile,with_tail=False),('menu mismatch',route)
 assert len(d.xpath('//*[@data-map-src]'))==1 and not d.xpath('//iframe'),('map eager load',route)
 assert len(d.xpath('//script[contains(@src,"shared-components.js")]'))==1,route
 for a in d.xpath('//a[contains(@href,"yandex.ru/maps/")]'):
  assert a.get('target')=='_blank' and 'noopener' in a.get('rel',''),(route,a.attrib)
print(json.dumps({'pages':len(routes),'identical_header_footer':True,'desktop_burger_same_tree':True,'maps_deferred':True,'errors':[]},ensure_ascii=False,indent=2))
