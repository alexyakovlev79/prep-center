from pathlib import Path
from lxml import html
from urllib.parse import urlsplit,unquote
import json,csv,hashlib
R=Path(__file__).parent;site=(R/'site').resolve();provenance=json.loads((R/'source/ten-provenance.json').read_text());new={x['path']:x for x in provenance};errors=[];graph={}
for p in [site/'index.html',*site.glob('*/index.html')]:
 d=html.fromstring(p.read_bytes());key='/' if p.parent==site else '/'+p.parent.name+'/';graph[key]=set();assert len(d.xpath('//h1'))==1
 for e in d.xpath('//*[@href or @src]'):
  u=e.get('href') or e.get('src');s=urlsplit(u)
  if s.scheme or u.startswith('//'):continue
  f=(p.parent/unquote(s.path)).resolve() if s.path else p
  if f.is_dir():f=f/'index.html'
  if not f.exists():errors.append((key,u));continue
  if f.name=='index.html':graph[key].add('/' if f.parent==site else '/'+f.parent.name+'/')
  if s.fragment and f.suffix=='.html' and not html.fromstring(f.read_bytes()).xpath('//*[@id=$id]',id=s.fragment):errors.append((key,u))
 if key in new:
  a=d.xpath('//article')[0];assert len(a.xpath('.//img'))==3 and len(a.xpath('.//details'))==new[key]['faq'];assert '[[AGENT' not in a.text_content();assert not d.xpath('//form|//script[not(@type="application/ld+json")]')
  for script in d.xpath('//script[@type="application/ld+json"]'):json.loads(script.text)
assert not errors,errors
seen={'/'}
while True:
 n=seen|set.union(*(graph[x] for x in seen))
 if n==seen:break
 seen=n
assert len(seen)==21,(len(seen),set(graph)-seen)
assert all(any(route in v for k,v in graph.items() if k!=route) for route in new)
(R/'ten-link-map.json').write_text(json.dumps({k:sorted(v) for k,v in graph.items()},ensure_ascii=False,indent=2))
inv=json.loads((R/'ten-inventory-base.json').read_text())
for x in inv:
 if x['path'] in new:
  p=new[x['path']];x['status']=f"Сверстана; 3 существующих фото, {p['faq']} FAQ; двусторонняя перелинковка";x['latest_capture']='Полный исходник 18.09.2026; поисковый индекс проверен 04.11.2026; полного октябрьского снимка нет';x['sources']=list(dict.fromkeys(x['sources']+[p['source_file']]))
(R/'page-inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2))
with (R/'page-inventory.csv').open('w',newline='',encoding='utf-8-sig') as f:
 fields=list(dict.fromkeys(k for x in inv for k in x));w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for row in inv:w.writerow({k:'; '.join(v) if isinstance(v,list) else v for k,v in row.items()})
note='''

## 04.11.2026: еще 10 страниц и перелинковка

Восстановлены FBS Wildberries, Ozon, Яндекс Маркет; FBL ЛЭТУАЛЬ; требования FBW Wildberries, FBO Ozon, FBY Яндекс Маркета и FBS трех площадок. Полные тексты — пакеты A/B/C/D от 18.09.2026. Поисковый индекс проверен 04.11.2026, полного октябрьского снимка этих страниц не найдено. Дата источника явно отделена от даты восстановления. Инструкции сохраняют ссылки на официальные регламенты и дату проверки исходника.

По 3 существующие фотографии на каждой странице, всего 66 FAQ. Новые изображения не генерировались. Поздняя индексная копия FBL дополнена доставкой на центральный склад ЛЭТУАЛЬ и отдельной машиной. Короб 150 ₽, паллетирование 400 ₽ по согласованным изменениям 20.10; предоставление паллета 500 ₽ сохранено отдельно. Из FBL убран неподтвержденный календарь законодательства о маркировке, сохранены операции и ссылка на услугу маркировки.

Услуги и требования связаны в обе стороны, FBO и FBS связаны по соответствующей площадке. На существующих страницах добавлены тематические обратные ссылки. На главной — блок по четырем маркетплейсам; раздел «Статьи» в общем меню ведет к инструкциям. Header и contact/footer берутся из канонического корневого index.html. Не восстановленные маршруты временно ведут на главную с сохранением исходной цели.

Проверено в предпросмотре: 10 desktop-страниц, фотографии 3/3, раскрытие FAQ; на ширине 390 px нет горизонтального переполнения, таблицы 349 px. Локальная проверка всех файлов, ссылок, якорей и JSON-LD успешна, все 21 страницы достижимы с главной. Публичная приемка выполняется после деплоя. Формы и калькулятор пока заменены контактами; noindex,follow сохранен до этапа запуска индексации.

Всего восстановлена 21 содержательная страница из 45, включая главную.
'''
for base,out in [('ten-readme-base.md','ten-readme.md'),('ten-log-base.md','ten-log.md')]: (R/out).write_text((R/base).read_text()+note)
p=R/'PAGE_INVENTORY.md';text=p.read_text();text=text.split('\n## 04.11.2026: еще 10 страниц и перелинковка')[0]
for route in new:
 text='\n'.join(line.replace('Ожидает восстановления','Сверстана; осенний исходник, фото, FAQ, двусторонние ссылки').replace('URL и следы в осеннем поисковом индексе / меню','Сверстана; осенний исходник, фото, FAQ, двусторонние ссылки') if '`'+route+'`' in line and line.startswith('|') else line for line in text.splitlines())
p.write_text(text+note)
files=[]
def add(path,p):
 b=p.read_bytes();files.append({'path':path,'local':str(p.resolve()),'sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'size':len(b)})
for p in [site/'index.html',*site.glob('*/index.html')]:add(str(p.relative_to(site)),p)
add('assets/recovery-links.css',site/'assets/recovery-links.css')
for n in ['build_ten.py','prepare_ten.py','PAGE_INVENTORY.md','page-inventory.json','page-inventory.csv','ten-link-map.json']:add('restoration/'+n,R/n)
for x in provenance:add('restoration/source/'+x['source_file'],R/'source'/x['source_file'])
for n in ['ten-indexed-evidence.txt','ten-late-evidence.txt','ten-provenance.json']:add('restoration/source/'+n,R/'source'/n)
add('README.md',R/'ten-readme.md');add('restoration/RESTORE_LOG.md',R/'ten-log.md')
(R/'ten-upload-manifest.json').write_text(json.dumps(files,ensure_ascii=False,indent=2));print('PASS: 21 reachable pages; candidate files:',len(files))
