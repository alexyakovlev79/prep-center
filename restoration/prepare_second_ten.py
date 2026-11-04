from pathlib import Path
from lxml import html
from urllib.parse import urlsplit,unquote
import json,csv,hashlib
R=Path(__file__).parent;site=(R/'site').resolve();src=R/'source/next-ten';prov=json.loads((src/'provenance.json').read_text());new={x['path']:x for x in prov};errors=[];graph={}
for p in [site/'index.html',*site.glob('*/index.html')]:
 d=html.fromstring(p.read_bytes());key='/' if p.parent==site else '/'+p.parent.name+'/';graph[key]=set();assert len(d.xpath('//h1'))==1,(key,'h1')
 for e in d.xpath('//*[@href or @src]'):
  u=e.get('href') or e.get('src');s=urlsplit(u)
  if s.scheme or u.startswith('//'):continue
  f=(p.parent/unquote(s.path)).resolve() if s.path else p
  if f.is_dir():f=f/'index.html'
  if not f.exists():errors.append((key,u));continue
  if f.name=='index.html':graph[key].add('/' if f.parent==site else '/'+f.parent.name+'/')
  if s.fragment and f.suffix=='.html' and not html.fromstring(f.read_bytes()).xpath('//*[@id=$i]',i=s.fragment):errors.append((key,u))
 for sc in d.xpath('//script[@type="application/ld+json"]'):json.loads(sc.text)
 if key in new:
  a=d.xpath('//main/article')[0];assert len(a.xpath('.//img'))==new[key]['images'];assert len(a.xpath('.//details'))==new[key]['faq'];assert not a.xpath('.//form|.//script');assert '[[AGENT' not in a.text_content() and '[ИЗОБРАЖЕНИЕ' not in a.text_content()
  assert d.xpath('//meta[@name="robots"]/@content')==['noindex,follow']
assert not errors,errors
seen={'/'}
while True:
 n=seen|set.union(*(graph[x] for x in seen))
 if n==seen:break
 seen=n
assert len(seen)==31,(len(seen),set(graph)-seen)
assert all(any(route in v for k,v in graph.items() if k!=route) for route in new)
(src/'link-map.json').write_text(json.dumps({k:sorted(v) for k,v in graph.items()},ensure_ascii=False,indent=2))
inv=json.loads((R/'page-inventory.json').read_text())
for x in inv:
 if x['path'] in new:
  z=new[x['path']];x['status']=f"Сверстана; {z['images']} изображений, {z['faq']} FAQ; двусторонние тематические ссылки"
  x['latest_capture']='Полный HTML 22.08.2026; поздний поисковый индекс проверен 04.11.2026'
  if x['path']=='/about/':x['latest_capture']+='; восстановлены изменения 21.10.2026'
  elif x['path']=='/wms-mpfit-dlya-fulfillmenta/':x['latest_capture']='Полный исходный текст 05.09.2026; 10 снимков экрана; восстановлены индексные блоки 20.10.2026, полный октябрьский HTML не получен'
  elif x['path']=='/trebovaniya-fbl-letual/':x['latest_capture']='Полный исходный текст 18.09.2026'
  elif x['path']=='/contacts/':x['latest_capture']='Реконструкция по подтвержденным контактам главной; банковское содержимое старого архива исключено'
(R/'page-inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2))
with (R/'page-inventory.csv').open('w',newline='',encoding='utf-8-sig') as f:
 fields=list(dict.fromkeys(k for x in inv for k in x));w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for row in inv:w.writerow({k:'; '.join(v) if isinstance(v,list) else v for k,v in row.items()})
note='''

## 04.11.2026: вторая группа из 10 страниц

Восстановлены `/fulfillment-shampuni-geli/`, `/fulfillment-bytovaya-himiya/`, `/fulfillment-kosmetika/`, `/fulfillment-avtohimiya/`, `/fulfillment-stroitelnaya-himiya/`, `/srochnaya-obrabotka-partiy/`, `/about/`, `/contacts/`, `/trebovaniya-fbl-letual/`, `/wms-mpfit-dlya-fulfillmenta/`.

У семи страниц использован полный HTML-снимок 22.08.2026 с сохранением исходного компонента и его стилей. Дата самого снимка отделена от даты публикации страницы. Для «О компании» поздний индекс подтверждает обновление 21.10.2026: добавлено связывание КИЗ вложений с кодом набора и дублирование КИЗ одной единицы. Полный текст WMS получен из исходного документа 05.09; добавлены подтвержденные индексом блоки обновления 20.10 о дублировании и сопоставлении КИЗ набора. Десять подготовленных снимков экрана из исходного пакета распределены по статье и открываются крупнее. Полный октябрьский HTML не найден. Требования FBL восстановлены из исходного MD 18.09.2026; дата проверки не выдается за текущую.

На новых страницах 45 изображений и 59 FAQ. Найдены исходные фотографии косметики и 7 фото из пакета «О Преп-Центре». Изображения автохимии и строительной химии дополнены существующими реальными фото склада и упаковки. На странице бытовой химии вместо недоступного фото порошка размещен общий снимок приемки с точной подписью, без заявления, что это тот же проект. Новые изображения и логотипы не генерировались. Для двух страниц исправлена нулевая ширина отложенно загружаемых фото в исходных стилях.

В архиве `/contacts/` найдены текст, телефоны и карта банковского шаблона. Они не перенесены. Контакты реконструированы из действующей главной: Пушкино, Новая, 10; +7 (930) 600 75 20; info@prep-center.ru; @prepmanager2; ежедневно 08:00–20:00. Старая статья `/upakovka-bytovoy-khimii/` отложена, вместо нее в пакет взят актуальный материал WMS.

Ссылки на новые страницы активированы по сохраненным исходным целям; добавлены тематические обратные переходы со страниц FBO, FBS, жидких товаров, упаковки, этикеток, маркировки и наборов. ЛЭТУАЛЬ FBL и инструкция связаны в обе стороны. На главной добавлен блок категорий и работы склада, в общем меню восстановлено «О компании», в подвале добавлены контакты. Общая шапка и подвал распространяются из канонического корневого index.html. На главной исправлены ссылки на Telegram и контакты.

Проверка структуры, локальных ресурсов, якорей и JSON-LD успешна: 31 содержательная страница достижима с главной. Предпросмотр на 390 px: без горизонтального переполнения, таблицы 349 px; загрузка фото и FAQ проверяются отдельно. Публичная приемка фиксируется после публикации. Формы и калькулятор пока заменены контактами. `noindex,follow` сохранен до отдельного этапа запуска индексации.

Всего восстановлена 31 содержательная страница из 45, включая главную.
'''
for name in ['README.md','RESTORE_LOG.md','PAGE_INVENTORY.md']:
 p=(R/'site/README.md') if name=='README.md' else R/name
 s=p.read_text().split('\n## 04.11.2026: вторая группа из 10 страниц')[0]
 if name=='PAGE_INVENTORY.md':
  for route in new:s='\n'.join(line.replace('Ожидает восстановления','Сверстана; фото, FAQ и тематические ссылки').replace('URL и следы в осеннем поисковом индексе / меню','Сверстана; фото, FAQ и тематические ссылки') if '`'+route+'`' in line and line.startswith('|') else line for line in s.splitlines())
 p.write_text(s+note)
files=[]
def add(path,p):
 b=p.read_bytes();files.append({'path':path,'local':str(p.resolve()),'sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'size':len(b),'binary':p.suffix in ['.webp','.woff2']})
for p in [site/'index.html',*site.glob('*/index.html')]:add(str(p.relative_to(site)),p)
for p in (site/'assets').glob('*'):add('assets/'+p.name,p)
for n in ['build_second_ten.py','prepare_second_ten.py','PAGE_INVENTORY.md','page-inventory.json','page-inventory.csv','RESTORE_LOG.md']:add('restoration/'+n,R/n)
for p in src.glob('*'):
 if p.suffix in ['.html','.md','.txt','.json'] and not p.name.startswith(('contacts-','upakovka-')):add('restoration/source/next-ten/'+p.name,p)
for n in ['next-ten-search-evidence.txt','next-ten-late-evidence.txt']:add('restoration/source/'+n,R/'source'/n)
add('README.md',site/'README.md');(R/'second-ten-upload-manifest.json').write_text(json.dumps(files,ensure_ascii=False,indent=2));print('PASS: 31 reachable pages,',sum(z['images'] for z in prov),'images,',sum(z['faq'] for z in prov),'FAQ')
