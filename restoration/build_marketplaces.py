from pathlib import Path
from lxml import html,etree
from copy import deepcopy
from PIL import Image
import re,json,html as esc
R=Path(__file__).parent;S=R/'source';SITE=R.parent if (R.parent/'index.html').exists() else R/'site'
# Root index.html remains canonical for shared header and contact/footer.
helper=(R/'build_next3.py').read_text();exec(helper[helper.index('LIVE='):helper.index('# Activate only')])
PAGES=[('fbo-wildberries','01_page_fbo_wildberries.md','WB / FBW','wb','warehouse-facade.webp','Склад Преп-Центра и зона отгрузки'),('fbo-ozon','02_page_fbo_ozon.md','Ozon / FBO','ozon','fbo-03.webp','Паллеты и короба на складе Преп-Центра'),('fby-yandex-market','03_page_fby_yandex_market.md','Яндекс Маркет / FBY','yandex','fbo-02.webp','Приемка товара на складе Преп-Центра')]
LIVE.update('/'+x[0]+'/' for x in PAGES)
header=home.xpath('//header')[0];contact=home.xpath('//*[@id="contact"]')[0]
def inline(t):
 t=esc.escape(t.replace('ё','е'));return re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',t)
def parse_md(md):
 root=etree.Element('div');lines=md.strip().splitlines();i=0
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line.startswith('#'):
   m=re.match(r'(#{2,3}) (.+)',line);e=etree.SubElement(root,'h'+str(len(m[1])));set_fragment(e,inline(m[2]));i+=1;continue
  if re.match(r'^(- |\d+\. )',line):
   ordered=bool(re.match(r'^\d+\.',line));ul=etree.SubElement(root,'ol' if ordered else 'ul')
   while i<len(lines) and re.match(r'^(- |\d+\. )',lines[i].strip()):
    li=etree.SubElement(ul,'li');set_fragment(li,inline(re.sub(r'^(- |\d+\. )','',lines[i].strip())));i+=1
   continue
  p=[]
  while i<len(lines) and lines[i].strip() and not re.match(r'^(#{2,3} |[-] |\d+\. )',lines[i].strip()):p.append(lines[i].strip());i+=1
  e=etree.SubElement(root,'p');set_fragment(e,inline(' '.join(p)))
 return root

def picture(name,alt,hero=False):
 w,h=Image.open(SITE/'assets'/name).size
 fig=etree.Element('figure',{'class':'marketplace-photo'})
 etree.SubElement(fig,'img',src='../assets/'+name,alt=alt,width=str(w),height=str(h),loading='eager' if hero else 'lazy',decoding='async',style=f'aspect-ratio:{w}/{h}',**{'class':'fboservice__hero-image' if hero else 'fboservice__image'})
 if not hero:etree.SubElement(fig,'figcaption').text=alt+'.'
 return fig

provenance=[]
for slug,file,market,key,heroimg,heroalt in PAGES:
 raw=(S/file).read_text();meta={k:re.search(r'\*\*'+k+r':\*\* (.+)',raw)[1].strip() for k in ['H1','Title','Description']};body=raw.split('\n---\n',1)[1]
 body=re.sub(r'\[\[AGENT:[^\]]*\]\]',lambda m:'<TARIFF_LINK>' if m.group(0).strip()=='[[AGENT: /tarify/]]' else '',body,flags=re.S)
 body=body.replace('<TARIFF_LINK>','актуальные тарифы и график отгрузок')
 # Only confirmed October changes, keeping the separate pallet supply tariff.
 body=body.replace('120 ₽','150 ₽').replace('300 ₽','400 ₽')
 body=body.replace('Актуальный график хранится в разделе .','Актуальный график подтверждаем перед созданием поставки.')
 body=body.replace('Доставка возможна по индивидуальному расчету. В текущем регулярном публичном графике Преп-Центра фиксированные маршруты Яндекс Маркета не опубликованы, поэтому склад и дату нужно согласовать отдельно.','Да. Доставляем через транзитный склад в Мытищах и напрямую на Софьино-1. Стоимость зависит от числа коробов или паллет; дату выезда подтверждаем по созданной поставке и доступному слоту.')
 if key=='yandex':
  start=body.index('### 6. Передача на Яндекс Маркет');end=body.index('\n## ',start);body=body[:start]+'''### 6. Передача на Яндекс Маркет

После подготовки поставку можно забрать со склада Преп-Центра или согласовать доставку на транзитный либо основной склад Маркета. Короба, паллеты и ярлыки готовим по созданной заявке.
'''+body[end:]
  body=body.replace('Для Яндекс Маркета регулярный фиксированный маршрут в текущем публичном графике Преп-Центра не заявлен','Доставку согласуем по выбранному складу и доступному слоту')
  body=body.replace('Для Яндекс Маркета доставку рассчитываем индивидуально под склад, дату и объем.','Доставляем через транзитный склад в Мытищах и напрямую на Софьино-1. Дату выезда подтверждаем по созданной поставке и доступному слоту.')
  body=body.replace('Эти кейсы подтверждают операции и производительность Преп-Центра; не утверждаем, что конкретные партии из списка отгружались именно на Яндекс Маркет, если это не указано на странице кейса.','Эти кейсы показывают, как Преп-Центр выстраивает обработку крупных партий: от приемки и сортировки до упаковки, маркировки и формирования поставок.')
 if key=='wb':body=body.replace('Преп-Центр уже публикует реальные кейсы с крупными партиями и несколькими операциями. Конкретный маркетплейс в кейсе указываем только там, где он подтвержден; эти примеры показывают производственные возможности склада.','В кейсах Преп-Центра представлены крупные партии и последовательная обработка товара на складе.')
 # Newer indexed delivery content, ahead of the price section.
 heading={'wb':'## Сколько стоит подготовка поставки','ozon':'## Стоимость подготовки FBO Ozon','yandex':'## Сколько стоит подготовка'}[key]
 body=body.replace(heading,(S/(key+'-late-delivery.md')).read_text()+'\n'+heading)
 parsed=parse_md(body);intro=[]
 while len(parsed) and parsed[0].tag=='p':intro.append(parsed[0]);parsed.remove(parsed[0])
 article=etree.Element('article',{'class':'fboservice marketplace-restored'});container=etree.SubElement(article,'div',{'class':'fboservice__container'})
 crumb=etree.SubElement(container,'nav',{'class':'fboservice__breadcrumbs','aria-label':'Хлебные крошки'});crumb.append(html.fromstring('<a href="/">Главная</a>'));etree.SubElement(crumb,'span').text='→';crumb.append(html.fromstring('<a href="/fulfillment-fbo/">FBO-фулфилмент</a>'));etree.SubElement(crumb,'span').text='→ '+market
 hero=etree.SubElement(container,'section',{'class':'fboservice__hero'});copy=etree.SubElement(hero,'div');etree.SubElement(copy,'p',{'class':'fboservice__recovery-date'}).text='Опубликовано: 18 сентября 2026 · Восстановлено: 4 ноября 2026';etree.SubElement(copy,'h1').text=meta['H1']
 for j,p in enumerate(intro):
  if j==0:p.set('class','fboservice__lead')
  copy.append(p)
 actions=etree.SubElement(copy,'div',{'class':'fboservice__actions'});actions.append(html.fromstring('<a class="fboservice__button" href="#contact">Обсудить поставку</a>'));actions.append(html.fromstring('<a class="fboservice__button fboservice__button--ghost" href="https://t.me/prepmanager2">Написать в Telegram</a>'));hero.append(picture(heroimg,heroalt,True))
 current=None;faqmode=False;faq=[];faqitem=None
 for e in list(parsed):
  if e.tag=='h2':
   current=etree.SubElement(container,'section',{'class':'fboservice__section'});current.append(e);faqmode=label(e)=='Частые вопросы'
   if faqmode:current.set('class','fboservice__section fboservice__faq')
  elif current is None:
   if e.tag=='h3':e.tag='h2'
   if current is None:current=etree.SubElement(container,'section',{'class':'fboservice__section'})
   current.append(e)
  elif faqmode:
   if e.tag=='h3':
    faqitem=etree.SubElement(current,'details');etree.SubElement(faqitem,'summary').text=label(e)
   else:faqitem.append(e)
  else:current.append(e)
 # Present later delivery destinations as cards while retaining their full text.
 for delivery in container.xpath('./section'):
  hs=delivery.xpath('./h2')
  if not hs or not ('доставки' in label(hs[0]) or label(hs[0])=='Доставка FBY на Яндекс Маркет'):continue
  grid=None;card=None
  for el in list(delivery):
   if el.tag=='h3':
    if grid is None:grid=etree.SubElement(delivery,'div',{'class':'fboservice__grid marketplace-routes'})
    card=etree.SubElement(grid,'div',{'class':'fboservice__card'});delivery.remove(el);card.append(el)
   elif card is not None and el is not grid:delivery.remove(el);card.append(el)
 # Integrate real operational photographs, no claim that a photo is a delivery to this marketplace.
 sections=container.xpath('./section[contains(@class,"fboservice__section")]');sections[1].append(picture('packing-line.webp','Упаковочная линия Преп-Центра'));sections[-3].append(picture('fbo-03.webp' if heroimg!='fbo-03.webp' else 'fbo-02.webp','Подготовка и хранение партии на складе Преп-Центра'))
 # Prices become a compact table; a saved source list remains source evidence.
 price=next(sec for sec in sections if sec.xpath('./h2') and label(sec.xpath('./h2')[0]) in ['Сколько стоит подготовка поставки','Стоимость подготовки FBO Ozon','Сколько стоит подготовка'])
 uls=price.xpath('./ul')
 if uls:
  ul=uls[0];wrap=etree.Element('div',{'class':'fboservice__table-wrap'});tb=etree.SubElement(wrap,'table',{'class':'fboservice__table'});tr=etree.SubElement(etree.SubElement(tb,'thead'),'tr');etree.SubElement(tr,'th',scope='col').text='Операция';etree.SubElement(tr,'th',scope='col').text='Цена, без НДС';tbody=etree.SubElement(tb,'tbody')
  for li in ul:
   t=label(li);parts=re.split(r'\s[—–]\s',t,maxsplit=1);assert len(parts)==2,t
   tr=etree.SubElement(tbody,'tr');etree.SubElement(tr,'td').text=parts[0];etree.SubElement(tr,'td').text=parts[1].rstrip('; .')
  ul.getparent().replace(ul,wrap)
 # Primary marketplace reference and existing restored services.
 official={'wb':('https://seller.wildberries.ru/instructions/ru/ru/material/step-three-fbw-shipment-preparation','Правила подготовки поставки Wildberries'),'ozon':('https://seller-edu.ozon.ru/contract-for-sellers/regulations-fbo/reglament-postavok-na-fulfilment','Регламент поставок Ozon FBO'),'yandex':('https://yandex.ru/support/marketplace/ru/storage/shipment/preparation/packaging','Упаковка товаров и палет Яндекс Маркета')}[key]
 note=html.fromstring(f'<aside class="fboservice__note"><p>Перед запуском партии сверяем требования выбранного склада и параметры созданной поставки.</p><a href="{official[0]}" target="_blank" rel="noopener">{official[1]}</a></aside>');hero.addnext(note)
 links=etree.SubElement(container,'section',{'class':'fboservice__section'});etree.SubElement(links,'h2').text='Связанные услуги';grid=etree.SubElement(links,'div',{'class':'fboservice__grid fboservice__grid--3'})
 targets=[('/fulfillment-fbo/','Все направления FBO'),('/fulfillment-fbs/','FBS-фулфилмент'),('/termousadka-vpp/','Термоусадка и ВПП'),('/etiketki-marketpleysov/','Этикетки маркетплейсов'),('/chestnyy-znak/','Честный знак'),('/komplektatsiya-naborov/','Комплектация наборов')]+[('/'+p[0]+'/',p[2]) for p in PAGES if p[0]!=slug]
 for href,title in targets:grid.append(html.fromstring(f'<a class="fboservice__card" href="{href}">{title}</a>'))
 cta=etree.SubElement(container,'section',{'class':'fboservice__cta'});etree.SubElement(cta,'h2').text='Рассчитаем вашу поставку';etree.SubElement(cta,'p').text='Пришлите фотографии товара, количество единиц и SKU, список операций и планируемую дату. Менеджер рассчитает стоимость и срок обработки партии.';cta.append(html.fromstring('<a class="fboservice__button" href="#contact">Обсудить поставку</a>'))
 resolve_links(article)
 head=deepcopy(home.xpath('//head')[0]);head.xpath('./title')[0].text=meta['Title'];head.xpath('./meta[@name="description"]')[0].set('content',meta['Description']);head.xpath('./link[@rel="canonical"]')[0].set('href','https://prep-center.ru/'+slug+'/')
 for e in head.xpath('.//*[@href]'):
  if e.get('href','').startswith('./assets/'):e.set('href','.'+e.get('href'))
 for e in head.xpath('./link[@rel="preload"][@as="image"]'):e.set('href','../assets/'+heroimg)
 etree.SubElement(head,'link',rel='stylesheet',href='../assets/fulfillment-fbo.css');etree.SubElement(head,'link',rel='stylesheet',href='../assets/marketplace-restored.css')
 for prop,value in [('og:title',meta['Title']),('og:description',meta['Description']),('og:url','https://prep-center.ru/'+slug+'/'),('og:type','website'),('og:image','https://prep-center.ru/assets/'+heroimg)]:
  old=head.xpath('./meta[@property=$p]',p=prop)
  if old:old[0].set('content',value)
  else:etree.SubElement(head,'meta',property=prop,content=value)
 doc=etree.Element('html',lang='ru');doc.append(head);b=etree.SubElement(doc,'body');b.append(common(header));main=etree.SubElement(b,'main');main.append(article);main.append(common(contact))
 faq=[{'@type':'Question','name':label(it.xpath('./summary')[0]),'acceptedAnswer':{'@type':'Answer','text':' '.join(label(e) for e in it if e.tag!='summary')}} for it in article.xpath('.//details')]
 nodes=[{'@type':'Service','@id':'https://prep-center.ru/'+slug+'/#service','url':'https://prep-center.ru/'+slug+'/','name':meta['H1'],'serviceType':meta['H1'],'provider':{'@id':'https://prep-center.ru/#organization'},'areaServed':'Москва и Московская область'},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Главная','item':'https://prep-center.ru/'},{'@type':'ListItem','position':2,'name':'FBO-фулфилмент','item':'https://prep-center.ru/fulfillment-fbo/'},{'@type':'ListItem','position':3,'name':market,'item':'https://prep-center.ru/'+slug+'/'}]},{'@type':'FAQPage','mainEntity':faq}]
 for n in nodes:sc=etree.SubElement(b,'script',type='application/ld+json');sc.text=json.dumps({'@context':'https://schema.org',**n},ensure_ascii=False,separators=(',',':'))
 out=SITE/slug/'index.html';out.parent.mkdir(exist_ok=True);out.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html')+'\n')
 provenance.append(dict(slug=slug,source_package='Prep-Center_month3_PackageA_2026-09-18(1).zip',source_file=file,source_date='2026-09-18',indexed_check='2026-11-04',freshness='Late indexed delivery sections restored; no complete October HTML obtained',confirmed_price_changes='2026-10-20: box 150 RUB; palletization 400 RUB; pallet supply 500 RUB unchanged',images=3,faq=len(faq),generated_images=0))
# Restore the marketplace links on homepage and FBO hub.
for link in home.xpath('//a'):
 target={'Wildberries':'/fbo-wildberries/','Ozon':'/fbo-ozon/','Яндекс Маркет':'/fby-yandex-market/'}.get(label(link))
 if target:link.set('href','.'+target);link.set('data-original-href',target)
(SITE/'index.html').write_text('<!doctype html>\n'+html.tostring(home,encoding='unicode',method='html')+'\n')
for slug in ['fulfillment-zhidkih-tovarov','fulfillment-fbo','fulfillment-fbs','termousadka-vpp','chestnyy-znak','etiketki-marketpleysov','komplektatsiya-naborov']:
 p=SITE/slug/'index.html';doc=html.fromstring(p.read_bytes());resolve_links(doc.xpath('//article')[0])
 if slug=='fulfillment-fbo':
  a=doc.xpath('//article')[0];container=a[0];sec=etree.Element('section',{'class':'fboservice__section','id':'marketplace-directions'});etree.SubElement(sec,'h2').text='Поставки на склады маркетплейсов';gr=etree.SubElement(sec,'div',{'class':'fboservice__grid fboservice__grid--3'})
  for slug2,_,name,*_ in PAGES:gr.append(html.fromstring(f'<a class="fboservice__card" href="../{slug2}/">{name}</a>'))
  if not a.xpath('.//*[@id="marketplace-directions"]'):container.insert(2,sec)
 p.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html')+'\n')
(SITE/'assets/marketplace-restored.css').write_text('''.marketplace-routes h3{padding:0!important;background:none!important;margin:0 0 16px!important}.marketplace-photo{margin:0;min-width:0}.marketplace-photo figcaption{text-align:center;font-size:14px;color:#5e6b78;margin:12px 0 0}.marketplace-restored h3{margin-top:30px}.marketplace-restored h3:first-child{margin-top:0}.marketplace-restored .fboservice__hero>div>p:not(.fboservice__recovery-date){margin-bottom:18px}.marketplace-restored .fboservice__grid a{text-decoration:none!important;font-weight:700}.marketplace-restored .fboservice__card:hover{border-color:#f56a12}.marketplace-restored figure img{max-width:100%;display:block}.marketplace-restored .fboservice__table td{vertical-align:top}.marketplace-restored .fboservice__section>h3{padding:16px 20px;background:#f3f8fb;border-radius:14px;margin-top:28px}.marketplace-restored .fboservice__section>ul{margin-bottom:24px}@media(max-width:640px){.marketplace-restored .fboservice__hero{display:flex;flex-direction:column;align-items:stretch}.marketplace-restored .fboservice__hero>figure{order:-1}.marketplace-restored .fboservice__hero h1{font-size:34px}.marketplace-restored .fboservice__table td:last-child{overflow-wrap:normal}.marketplace-restored .fboservice__button{text-align:center}}
''')
(S/'marketplaces-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2));print(json.dumps(provenance,ensure_ascii=False))
