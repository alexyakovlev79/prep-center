from pathlib import Path
from lxml import html,etree
from copy import deepcopy
from PIL import Image
import re,json,html as esc
R=Path(__file__).parent;S=R/'source';SITE=R/'site'
helper=(R/'build_next3.py').read_text();exec(helper[helper.index('LIVE='):helper.index('# Activate only')])
FILES={p.name:p for p in (S/'batch10').rglob('*.md')}
PAGES=[
('fbs-wildberries','01_page_fbs_wildberries.md','Wildberries · FBS','fbo-wildberries','trebovaniya-fbs-wildberries','warehouse-aisle.webp'),
('fbs-ozon','02_page_fbs_ozon.md','Ozon · FBS','fbo-ozon','trebovaniya-fbs-ozon','fbo-02.webp'),
('fbs-yandex-market','03_page_fbs_yandex_market.md','Яндекс Маркет · FBS','fby-yandex-market','trebovaniya-fbs-yandex-market','warehouse-facade.webp'),
('fbl-letual','04_page_fbl_letual.md','ЛЭТУАЛЬ · FBL','fulfillment-fbo','chestnyy-znak','kits-01.webp'),
('trebovaniya-fbw-wildberries','01_info_wildberries_fbw_requirements.md','Требования Wildberries · FBW','fbo-wildberries','trebovaniya-fbs-wildberries','fbo-03.webp'),
('trebovaniya-fbo-ozon','02_info_ozon_fbo_requirements.md','Требования Ozon · FBO','fbo-ozon','trebovaniya-fbs-ozon','fbo-02.webp'),
('trebovaniya-fby-yandex-market','03_info_yandex_market_fby_requirements.md','Требования Яндекс Маркета · FBY','fby-yandex-market','trebovaniya-fbs-yandex-market','fbo-03.webp'),
('trebovaniya-fbs-wildberries','01_info_fbs_wildberries.md','Требования Wildberries · FBS','fbs-wildberries','trebovaniya-fbw-wildberries','warehouse-aisle.webp'),
('trebovaniya-fbs-ozon','02_info_fbs_ozon.md','Требования Ozon · FBS','fbs-ozon','trebovaniya-fbo-ozon','fbo-02.webp'),
('trebovaniya-fbs-yandex-market','03_info_fbs_yandex_market.md','Требования Яндекс Маркета · FBS','fbs-yandex-market','trebovaniya-fby-yandex-market','warehouse-facade.webp')]
LIVE.update('/'+p.parent.name+'/' for p in SITE.glob('*/index.html'));LIVE.update('/'+p[0]+'/' for p in PAGES)
TITLES={p[0]:p[2] for p in PAGES};TITLES.update({'fbo-wildberries':'Подготовка поставок Wildberries · FBW','fbo-ozon':'Подготовка поставок Ozon · FBO','fby-yandex-market':'Подготовка поставок Яндекс Маркет · FBY','fulfillment-fbo':'Все направления FBO','fulfillment-fbs':'FBS с единым остатком','termousadka-vpp':'Термоусадка и ВПП','chestnyy-znak':'Маркировка «Честный знак»','etiketki-marketpleysov':'Этикетки маркетплейсов','komplektatsiya-naborov':'Комплектация наборов','fulfillment-zhidkih-tovarov':'Подготовка жидких товаров'})
def inline(t):
 t=esc.escape(t.replace('ё','е'));t=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',t)
 def link(m):
  href=esc.unescape(m[2]);extra=' target="_blank" rel="noopener"' if href.startswith('https://') and 'prep-center.ru' not in href else ''
  return '<a href="'+esc.escape(href,quote=True)+'"'+extra+'>'+m[1]+'</a>'
 t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,t);return re.sub(r'`([^`]+)`',r'<code>\1</code>',t)
def parse(md):
 root=etree.Element('div');lines=md.splitlines();i=0
 while i<len(lines):
  t=lines[i].strip()
  if not t:i+=1;continue
  if t.startswith('|'):
   wrap=etree.SubElement(root,'div',{'class':'fboservice__table-wrap'});table=etree.SubElement(wrap,'table',{'class':'fboservice__table'});thead=etree.SubElement(table,'thead');tbody=etree.SubElement(table,'tbody');first=True
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=[v.strip() for v in lines[i].strip().strip('|').split('|')];i+=1
    if all(re.fullmatch(r':?-+:?',v) for v in cells):continue
    row=etree.SubElement(thead if first else tbody,'tr')
    for v in cells:
     e=etree.SubElement(row,'th' if first else 'td');set_fragment(e,inline(v))
     if first:e.set('scope','col')
    first=False
   continue
  m=re.match(r'^(#{2,3}) (.+)',t)
  if m:e=etree.SubElement(root,'h'+str(len(m[1])));set_fragment(e,inline(m[2]));i+=1;continue
  if re.match(r'^(- |\d+\. )',t):
   ul=etree.SubElement(root,'ol' if re.match(r'^\d+\.',t) else 'ul')
   while i<len(lines) and re.match(r'^(- |\d+\. )',lines[i].strip()):
    e=etree.SubElement(ul,'li');set_fragment(e,inline(re.sub(r'^(- |\d+\. )','',lines[i].strip())));i+=1
   continue
  p=[]
  while i<len(lines) and lines[i].strip() and not re.match(r'^(#{2,3} |[-] |\d+\. |\|)',lines[i].strip()):p.append(lines[i].strip());i+=1
  e=etree.SubElement(root,'p');set_fragment(e,inline(' '.join(p)))
 return root
def picture(name,alt,hero=False):
 w,h=Image.open(SITE/'assets'/name).size;fig=etree.Element('figure',{'class':'marketplace-photo'})
 etree.SubElement(fig,'img',src='../assets/'+name,alt=alt,width=str(w),height=str(h),loading='eager' if hero else 'lazy',decoding='async',style=f'aspect-ratio:{w}/{h}',**{'class':'fboservice__hero-image' if hero else 'fboservice__image'})
 if not hero:etree.SubElement(fig,'figcaption').text=alt
 return fig
def addlinks(container,slug,targets):
 existing=container.xpath('.//*[@id="recovery-related"]')
 for e in existing:e.getparent().remove(e)
 sec=etree.SubElement(container,'section',{'class':'fboservice__section','id':'recovery-related'});etree.SubElement(sec,'h2').text='Услуги и инструкции по теме';grid=etree.SubElement(sec,'div',{'class':'fboservice__grid fboservice__grid--3'})
 for target in dict.fromkeys(targets):
  if target==slug:continue
  a=etree.SubElement(grid,'a',{'class':'fboservice__card','href':'/'+target+'/'});a.text=TITLES[target]
 resolve_links(sec)
# Change shared navigation at the canonical root, then propagate that exact component.
for a in home.xpath('//header//a|//*[@id="contact"]//a'):
 if label(a)=='Статьи':a.set('href','./#marketplace-guides');a.set('data-original-href','/#marketplace-guides')
 if label(a).startswith('+7'):a.set('href','tel:+79306007520')
 if label(a)=='info@prep-center.ru':a.set('href','mailto:info@prep-center.ru')
 if label(a)=='Обсудить задачу':a.set('href','#contact')
for a in home.xpath('//a'):
 if label(a)=='ЛЭТУАЛЬ':a.set('data-original-href','/fbl-letual/');a.set('href','./fbl-letual/')
old=home.xpath('//*[@id="marketplace-guides"]')
for e in old:e.getparent().remove(e)
guide=etree.Element('section',{'class':'recovery-guides','id':'marketplace-guides'});etree.SubElement(guide,'h2').text='Маркетплейсы: услуги и требования';grid=etree.SubElement(guide,'div',{'class':'recovery-guides__grid'})
for market,slugs in [('Wildberries',['fbo-wildberries','fbs-wildberries','trebovaniya-fbw-wildberries','trebovaniya-fbs-wildberries']),('Ozon',['fbo-ozon','fbs-ozon','trebovaniya-fbo-ozon','trebovaniya-fbs-ozon']),('Яндекс Маркет',['fby-yandex-market','fbs-yandex-market','trebovaniya-fby-yandex-market','trebovaniya-fbs-yandex-market']),('ЛЭТУАЛЬ',['fbl-letual'])]:
 card=etree.SubElement(grid,'div');etree.SubElement(card,'h3').text=market
 for target in slugs:etree.SubElement(card,'a',href='./'+target+'/',**{'data-original-href':'/'+target+'/'}).text=TITLES[target]
home.xpath('//*[@id="contact"]')[0].addprevious(guide)
if not home.xpath('//link[@href="./assets/recovery-links.css"]'):etree.SubElement(home.xpath('//head')[0],'link',rel='stylesheet',href='./assets/recovery-links.css')
(SITE/'index.html').write_text('<!doctype html>\n'+html.tostring(home,encoding='unicode',method='html'))
header=home.xpath('//header')[0];contact=home.xpath('//*[@id="contact"]')[0];provenance=[]
for slug,file,short,paired,other,image in PAGES:
 source=S/file if slug=='fbl-letual' else FILES[file];raw=source.read_text();isinfo=slug.startswith('trebovaniya')
 if isinfo:
  def field(marker):return re.search(r'\[\[AGENT: '+marker+r'\]\]\s*(?:# )?([^\n]+)',raw)[1].strip()
  meta={'H1':field('H1'),'Title':field('SEO Title'),'Description':field('Meta Description')};body=re.sub(r'^\s*Проверено:[^\n]*\n','',raw.split('[[AGENT: видимый блок даты]]',1)[1],count=1)
 else:
  meta={k:re.search(r'\*\*'+k+r':\*\* (.+)',raw)[1].strip() for k in ['H1','Title','Description']};body=raw.split('\n---\n',1)[1]
 body=re.sub(r'\[\[AGENT:.*?\]\]','',body,flags=re.S).replace('от **120 ₽**','от **150 ₽**').replace('от **300 ₽**','от **400 ₽**')
 body=body.replace('Полный прайс: .','Точный состав операций и стоимость подтвердит менеджер.').replace('Все действующие цены — в тарифах Преп-Центра.','Точную стоимость дополнительных операций подтвердит менеджер.')
 body=body.replace('Эти параметры зависят от текущей настройки FBS и могут меняться, поэтому рабочий график сверяется с кабинетом клиента, а на странице не нужно обещать единый универсальный дедлайн для всех магазинов.','Эти параметры зависят от настройки FBS и могут меняться. Рабочий график сверяем с кабинетом клиента.')
 if slug=='fbl-letual':
  start=body.index('## Доставка в ЛЭТУАЛЬ');end=body.index('\n## ',start+3)
  body=body[:start]+'''## Доставка FBL в ЛЭТУАЛЬ

Подготовленную поставку можно забрать своим транспортом, передать перевозчику или заказать доставку Преп-Центра на центральный склад ЛЭТУАЛЬ.

### Центральный склад FBL

Москва, пос. Рязановское, пос. Знамя Октября, домовладение 51, корп. 5; для навигатора — 51/5.

Приемка по будням с 09:00 до 17:30. Дату и время подтверждаем по созданной FBL-поставке и доступному окну.

Паллеты: 4000 ₽ за первый, 3100 ₽ за следующий. Короба: от 2000 ₽ за 4, далее 500 ₽.

### Отдельная машина

Москва и Московская область. До 20 паллет и 20 тонн — 35000 ₽; возможно до 33 паллет. Каждый паллет сверх базового объема — 1500 ₽. Ожидание до 6 часов бесплатно, далее 1000 ₽/час.

Данные водителя и автомобиля заранее вносят в FBL для оформления пропуска. Все цены без НДС. Перед выездом подтверждаем склад, слот и стоимость.
'''+body[end:]
  body=body.replace('доставка — индивидуально.','доставка на центральный склад — от 2000 ₽ за 4 короба или от 4000 ₽ за первый паллет.')
  body=body.replace('Пока отдельный регулярный маршрут в публичном графике не заявлен. Доставку рассчитываем индивидуально под склад, слот и объем либо передаем готовую поставку выбранному перевозчику.','Доставляем на центральный склад FBL. Дату, слот, объем и стоимость подтверждаем по созданной поставке; также можно передать партию выбранному перевозчику.')
  body=body.replace('Это примеры возможностей склада. Не утверждаем, что перечисленные партии поставлялись именно в ЛЭТУАЛЬ, если это не зафиксировано в соответствующем кейсе.','Эти примеры показывают складские операции с косметикой, жидкими товарами и наборами.')
  # Keep service description; do not republish an unverified regulatory timetable as current legal advice.
  body=re.sub(r'По официальной базе знаний ЛЭТУАЛЬ, \*\*с 1 июля 2026 года\*\*.*?\n\n','Перед запуском сверяем обязательность маркировки по товарной группе и действующие правила передачи сведений в документах.\n\n',body,flags=re.S)
 parsed=parse(body);intro=[]
 while len(parsed) and parsed[0].tag=='p':intro.append(parsed[0]);parsed.remove(parsed[0])
 article=etree.Element('article',{'class':'fboservice marketplace-restored'});container=etree.SubElement(article,'div',{'class':'fboservice__container'})
 crumb=etree.SubElement(container,'nav',{'class':'fboservice__breadcrumbs','aria-label':'Хлебные крошки'});etree.SubElement(crumb,'a',href='/').text='Главная';etree.SubElement(crumb,'span').text='→';etree.SubElement(crumb,'a',href='/'+paired+'/').text=TITLES[paired];etree.SubElement(crumb,'span').text='→ '+short
 hero=etree.SubElement(container,'section',{'class':'fboservice__hero'});copy=etree.SubElement(hero,'div');etree.SubElement(copy,'p',{'class':'fboservice__recovery-date'}).text=('Проверено в исходнике: ' if isinfo else 'Опубликовано: ')+'18 сентября 2026 · Восстановлено: 4 ноября 2026';etree.SubElement(copy,'h1').text=meta['H1']
 for i,p in enumerate(intro):
  if i==0:p.set('class','fboservice__lead')
  copy.append(p)
 actions=etree.SubElement(copy,'div',{'class':'fboservice__actions'});actions.append(html.fromstring('<a class="fboservice__button" href="#contact">Обсудить задачу</a>'));actions.append(html.fromstring('<a class="fboservice__button fboservice__button--ghost" href="https://t.me/prepmanager2">Написать в Telegram</a>'));hero.append(picture(image,'Товары и складские операции Преп-Центра',True))
 note=etree.SubElement(container,'aside',{'class':'fboservice__note'});etree.SubElement(note,'p').text=('Требования восстановлены по исходнику от 18.09.2026. Перед поставкой сверяйте действующий регламент в официальных источниках ниже и параметры заявки в кабинете продавца.' if isinfo else 'Состав работ, срок обработки и стоимость подтверждаем по вашей партии и техническому заданию.')
 sec=None;faqmode=False;faqitem=None
 for e in list(parsed):
  if e.tag=='h2' or (e.tag=='h3' and sec is None):
   e.tag='h2';sec=etree.SubElement(container,'section',{'class':'fboservice__section'});sec.append(e);faqmode=label(e)=='Частые вопросы'
   if faqmode:sec.set('class','fboservice__section fboservice__faq')
  elif faqmode:
   if e.tag=='h3':faqitem=etree.SubElement(sec,'details');etree.SubElement(faqitem,'summary').text=label(e)
   elif faqitem is not None:faqitem.append(e)
  else:
   if sec is None:sec=etree.SubElement(container,'section',{'class':'fboservice__section'})
   sec.append(e)
 sections=container.xpath('./section[contains(@class,"fboservice__section")]');sections[1].append(picture('packing-line.webp','Упаковочная линия Преп-Центра'));sections[-2].append(picture('labels-03.webp','Маркировка и упаковка товара на складе Преп-Центра'))
 # Contextual two-way service / reference link, distinct from the card directory.
 context=etree.SubElement(note,'p');context.text='По этой теме: ';a=etree.SubElement(context,'a',href='/'+paired+'/');a.text=TITLES[paired]
 targets=[paired,other,'fulfillment-fbs' if 'fbs' in slug else 'fulfillment-fbo','termousadka-vpp','etiketki-marketpleysov','chestnyy-znak','komplektatsiya-naborov'];addlinks(container,slug,targets);resolve_links(article)
 head=deepcopy(home.xpath('//head')[0]);head.xpath('./title')[0].text=meta['Title'];head.xpath('./meta[@name="description"]')[0].set('content',meta['Description']);head.xpath('./link[@rel="canonical"]')[0].set('href','https://prep-center.ru/'+slug+'/')
 for e in head.xpath('.//*[@href]'):
  if e.get('href','').startswith('./assets/'):e.set('href','.'+e.get('href'))
 for e in head.xpath('./link[@rel="preload"][@as="image"]'):e.set('href','../assets/'+image)
 for css in ['fulfillment-fbo.css','marketplace-restored.css']:etree.SubElement(head,'link',rel='stylesheet',href='../assets/'+css)
 for prop,value in [('og:title',meta['Title']),('og:description',meta['Description']),('og:url','https://prep-center.ru/'+slug+'/'),('og:type','article' if isinfo else 'website'),('og:image','https://prep-center.ru/assets/'+image)]:
  old=head.xpath('./meta[@property=$p]',p=prop)
  if old:old[0].set('content',value)
  else:etree.SubElement(head,'meta',property=prop,content=value)
 doc=etree.Element('html',lang='ru');doc.append(head);b=etree.SubElement(doc,'body');b.append(common(header));main=etree.SubElement(b,'main');main.append(article);main.append(common(contact))
 faq=[{'@type':'Question','name':label(it.xpath('./summary')[0]),'acceptedAnswer':{'@type':'Answer','text':' '.join(label(e) for e in it if e.tag!='summary')}} for it in article.xpath('.//details')]
 entity={'@type':'Article' if isinfo else 'Service','name':meta['H1'],'url':'https://prep-center.ru/'+slug+'/'}
 if isinfo:entity.update(headline=meta['H1'],datePublished='2026-09-18',author={'@type':'Organization','name':'Преп-Центр'})
 else:entity.update(provider={'@id':'https://prep-center.ru/#organization'},areaServed='Москва и Московская область')
 nodes=[entity,{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Главная','item':'https://prep-center.ru/'},{'@type':'ListItem','position':2,'name':short,'item':'https://prep-center.ru/'+slug+'/'}]},{'@type':'FAQPage','mainEntity':faq}]
 for n in nodes:sc=etree.SubElement(b,'script',type='application/ld+json');sc.text=json.dumps({'@context':'https://schema.org',**n},ensure_ascii=False)
 out=SITE/slug/'index.html';out.parent.mkdir(exist_ok=True);out.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html'))
 provenance.append({'path':'/'+slug+'/','source_file':str(source.relative_to(S)),'source_date':'2026-09-18','late_index_checked':'2026-11-04','complete_october_snapshot':False,'late_delivery_updated':slug=='fbl-letual','images':3,'faq':len(faq)})
# Activate original destinations throughout existing pages and add meaningful reverse links.
for p in SITE.glob('*/index.html'):
 slug=p.parent.name;doc=html.fromstring(p.read_bytes());article=doc.xpath('//article')[0]
 if slug not in [x[0] for x in PAGES]:
  targets=[]
  if slug in ['fbo-wildberries','fbo-ozon','fby-yandex-market']:
   map={'fbo-wildberries':['trebovaniya-fbw-wildberries','fbs-wildberries'],'fbo-ozon':['trebovaniya-fbo-ozon','fbs-ozon'],'fby-yandex-market':['trebovaniya-fby-yandex-market','fbs-yandex-market']};targets=map[slug]
  elif slug=='fulfillment-fbs':targets=[x[0] for x in PAGES if 'fbs' in x[0]]
  elif slug=='fulfillment-fbo':targets=['fbl-letual']+[x[0] for x in PAGES if x[0].startswith('trebovaniya') and 'fbs' not in x[0]]
  elif slug in ['termousadka-vpp','etiketki-marketpleysov','chestnyy-znak','komplektatsiya-naborov','fulfillment-zhidkih-tovarov']:targets=['fbl-letual','fbs-wildberries','fbs-ozon','fbs-yandex-market']
  if targets:
   addlinks(article[0],slug,targets)
   if not doc.xpath('//link[contains(@href,"fulfillment-fbo.css")]'):etree.SubElement(doc.xpath('//head')[0],'link',rel='stylesheet',href='../assets/fulfillment-fbo.css')
 resolve_links(article)
 old=doc.xpath('//header')[0];old.getparent().replace(old,common(header))
 oldcontact=doc.xpath('//*[@id="contact"]')[0];oldcontact.getparent().replace(oldcontact,common(contact))
 p.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html'))
(SITE/'assets/recovery-links.css').write_text('''.recovery-guides{max-width:1200px;margin:auto;padding:72px 24px;scroll-margin-top:120px}.recovery-guides h2{font-family:Oswald,sans-serif;font-size:clamp(30px,4vw,48px);margin:0 0 28px}.recovery-guides__grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}.recovery-guides__grid>div{background:white;border:1px solid #e5e9ee;border-radius:20px;padding:24px}.recovery-guides h3{font-size:23px;margin:0 0 18px}.recovery-guides a{display:block;color:#12648b;text-decoration:underline;margin-top:15px;line-height:1.5}.recovery-guides a:hover{color:#c64d00}#recovery-related .fboservice__card{display:block;text-decoration:none;font-weight:700}#recovery-related{scroll-margin-top:120px}@media(max-width:850px){.recovery-guides__grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:520px){.recovery-guides__grid{grid-template-columns:1fr}}''')
(S/'ten-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2));print(json.dumps(provenance,ensure_ascii=False))
