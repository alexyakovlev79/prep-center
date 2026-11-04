from pathlib import Path
from lxml import html,etree
from copy import deepcopy
from PIL import Image
import re,json,html as esc
R=Path(__file__).parent;S=R/'source';SRC=S/'next-ten';SITE=R/'site'
helper=(R/'build_next3.py').read_text();exec(helper[helper.index('LIVE='):helper.index('# Activate only')])
parser=(R/'build_ten.py').read_text();exec(parser[parser.index('def inline'):parser.index('# Change shared navigation')])
NAMES={'fulfillment-shampuni-geli':'Шампуни и гели','fulfillment-bytovaya-himiya':'Бытовая химия','fulfillment-kosmetika':'Косметика','fulfillment-avtohimiya':'Автохимия и автокосметика','fulfillment-stroitelnaya-himiya':'Строительная химия','srochnaya-obrabotka-partiy':'Срочная обработка партий','about':'О Преп-Центре','contacts':'Контакты','trebovaniya-fbl-letual':'Требования FBL ЛЭТУАЛЬ','wms-mpfit-dlya-fulfillmenta':'Складской учет в WMS МПФИТ'}
NEW=list(NAMES);LIVE.update('/'+p.parent.name+'/' for p in SITE.glob('*/index.html'));LIVE.update('/'+s+'/' for s in NEW)
TITLES={p.parent.name:label(html.fromstring(p.read_bytes()).xpath('//h1')[0]) for p in SITE.glob('*/index.html')};TITLES.update(NAMES)
CATEGORIES=NEW[:5]
def related(container,slug,targets):
 for e in container.xpath('./*[@id="second-recovery-related"]'):e.getparent().remove(e)
 sec=etree.SubElement(container,'section',{'class':'recovered-related','id':'second-recovery-related'});etree.SubElement(sec,'h2').text='Услуги и материалы по теме';gr=etree.SubElement(sec,'div',{'class':'recovered-related__grid'})
 for target in dict.fromkeys(targets):
  if target==slug:continue
  etree.SubElement(gr,'a',href='/'+target+'/').text=TITLES.get(target,target)
 resolve_links(sec)
def image_attrs(im,name,hero=False,alt=None):
 w,h=Image.open(SITE/'assets'/name).size
 for attr in ['srcset','data-src','data-srcset','style']:im.attrib.pop(attr,None)
 im.set('src','../assets/'+name);im.set('width',str(w));im.set('height',str(h));im.set('loading','eager' if hero else 'lazy');im.set('decoding','async');im.set('style',f'aspect-ratio:{w}/{h};height:auto')
 if alt:im.set('alt',alt)
def addphoto(container,name,alt):
 fig=etree.SubElement(container,'figure',{'class':'recovered-photo'});im=etree.SubElement(fig,'img',alt=alt);image_attrs(im,name);etree.SubElement(fig,'figcaption').text=alt;return fig
# Shared shell edited only here, at root.
for a in home.xpath('//a'):
 t=label(a)
 if t in ['О компании','Подробнее о Преп-Центре']:a.set('data-original-href','/about/');a.set('href','./about/')
 if t=='Контакты':a.set('data-original-href','/contacts/');a.set('href','./contacts/')
 if t.startswith('+7'):a.set('href','tel:+79306007520')
 elif t=='info@prep-center.ru':a.set('href','mailto:info@prep-center.ru')
 elif 'Telegram:' in t or t=='Записаться на экскурсию':a.set('href','https://t.me/prepmanager2')
 elif t in ['Начать сотрудничество','Рассчитать стоимость','Обсудить задачу']:a.set('href','#contact');a.set('data-original-href','#contact')
nav=home.xpath('//*[@id="contact"]//nav')[0]
if not any(label(a)=='Контакты' for a in nav.xpath('./a')):etree.SubElement(nav,'a',href='./contacts/',**{'data-original-href':'/contacts/'}).text='Контакты'
guide=home.xpath('//*[@id="marketplace-guides"]')[0];card=next(x for x in guide.xpath('./div/div') if x.xpath('./h3') and label(x.xpath('./h3')[0])=='ЛЭТУАЛЬ')
if not card.xpath('./a[@data-original-href="/trebovaniya-fbl-letual/"]'):etree.SubElement(card,'a',href='./trebovaniya-fbl-letual/',**{'data-original-href':'/trebovaniya-fbl-letual/'}).text='Требования FBL ЛЭТУАЛЬ'
for e in home.xpath('//*[@id="goods-and-warehouse"]'):e.getparent().remove(e)
sec=etree.Element('section',{'class':'recovery-guides','id':'goods-and-warehouse'});etree.SubElement(sec,'h2').text='Подготовка товаров и работа склада';gr=etree.SubElement(sec,'div',{'class':'recovery-guides__grid'})
for title,targets in [('Категории товаров',CATEGORIES[:3]),('Другие категории',CATEGORIES[3:]),('Работа склада',['srochnaya-obrabotka-partiy','wms-mpfit-dlya-fulfillmenta']),('Преп-Центр',['about','contacts'])]:
 c=etree.SubElement(gr,'div');etree.SubElement(c,'h3').text=title
 for t in targets:etree.SubElement(c,'a',href='./'+t+'/',**{'data-original-href':'/'+t+'/'}).text=NAMES[t]
guide.addnext(sec);resolve_links(home,True)
for e in home.xpath('//a[@data-original-href="#contact"]'):e.set('href','#contact')
(SITE/'index.html').write_text('<!doctype html>\n'+html.tostring(home,encoding='unicode',method='html'))
header=home.xpath('//header')[0];contact=home.xpath('//*[@id="contact"]')[0]
CSS='''/* Shared recovery additions, sourced by every changed page. */
.recovered-related{margin:56px 0 24px;padding:28px;background:#f3f8fb;border:1px solid #dfe7ed;border-radius:20px;color:#152333}.recovered-related h2{font:700 30px Tilda,sans-serif!important;line-height:1.25!important;margin:0 0 24px!important}.recovered-related__grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.recovered-related__grid a{display:flex;align-items:center;background:#fff;border:1px solid #dfe7ed;border-radius:14px;padding:18px;color:#075b8d;line-height:1.45;font:500 17px Tilda,sans-serif;text-decoration:none}.recovered-related__grid a:hover{border-color:#ff9800}.recovered-related__grid a:focus-visible{outline:3px solid #ff9800;outline-offset:3px}.recovered-photo{margin:28px 0;min-width:0}.recovered-photo img{width:100%;max-height:650px;object-fit:contain;border-radius:18px;display:block;background:#f3f8fb}.recovered-photo figcaption{color:#5e6b78;font:14px/1.6 Tilda,sans-serif;margin-top:12px;text-align:center}.recovered-date{font:14px/1.5 Tilda,sans-serif!important;color:#5e6b78;margin:12px 0 20px!important}.recovered-content img{max-width:100%;object-fit:contain}.recovered-content [class*=__hero]>*,.recovered-content [class*=__split]>*{min-width:0}.recovered-content li{margin-bottom:.5em}.recovered-content ul,.recovered-content ol{padding-left:1.3em}.recovered-content h3{font-family:Tilda,sans-serif}.recovered-content [class*=__hero-image]{max-height:530px;object-fit:contain!important}.recovered-content [class*=__photo] img{max-height:600px;object-fit:contain!important}.recovered-content [class*=__media-row] img{max-height:550px;object-fit:contain!important}.recovered-content table{max-width:100%;table-layout:fixed;width:100%}.recovered-content td,.recovered-content th{overflow-wrap:anywhere}.recovered-content p,.recovered-content li{overflow-wrap:break-word}.recovered-content [class*=__facts],.recovered-content [class*=__highlights]{padding-left:0;list-style:none}.recovered-content details summary{cursor:pointer}.wms-screenshot img{max-height:none!important}.wms-screenshot a{display:block}.wms-screenshot img{background:#fff}.recovered-content .marketplace-photo{margin-top:22px}.recovered-content .marketplace-photo img{max-height:650px}.recovered-content .fboservice__hero figure img{max-height:450px}.contact-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.contact-cards>div{padding:24px;border-radius:18px;background:#f3f8fb}.contact-cards h2{font-size:25px}.recovery-guides#goods-and-warehouse{padding-top:20px}.recovered-content [class*=__nowrap]{white-space:normal!important}
@media(max-width:700px){.recovered-related__grid,.contact-cards{grid-template-columns:1fr}.recovered-related{padding:20px}.recovered-related h2{font-size:25px!important}.recovered-content h1{overflow-wrap:anywhere;font-size:34px!important;line-height:1.2!important}.recovered-content img{height:auto!important;max-height:500px}.recovered-content [class*=__hero]{padding:24px 20px!important}.recovered-content [class*=__hero] img{max-height:390px}.recovered-content [class*=__button]{white-space:normal;text-align:center}.recovered-content .wms-screenshot img{max-height:none!important}}
'''
CSS+='\n.recovered-content .service-page__media-row img,.recovered-content .service-page__section>figure img{width:100%!important;height:auto!important}\n'
(SITE/'assets/second-recovery.css').write_text(CSS)
def shell(slug,article,title,desc,css,image,kind='Service',published=None,modified=None):
 article.set('class',article.get('class','')+' recovered-content');resolve_links(article)
 for e in article.iter():
  for k in list(e.attrib):
   if k.startswith(('data-agent','on')):del e.attrib[k]
 head=deepcopy(home.xpath('//head')[0]);head.xpath('./title')[0].text=title;head.xpath('./meta[@name="description"]')[0].set('content',desc);head.xpath('./link[@rel="canonical"]')[0].set('href','https://prep-center.ru/'+slug+'/')
 for e in head.xpath('.//*[@href]'):
  if e.get('href','').startswith('./assets/'):e.set('href','.'+e.get('href'))
 for e in head.xpath('./link[@rel="preload"][@as="image"]'):e.set('href','../assets/'+image)
 for f in [*css,'second-recovery.css']:etree.SubElement(head,'link',rel='stylesheet',href='../assets/'+f)
 for prop,value in [('og:title',title),('og:description',desc),('og:url','https://prep-center.ru/'+slug+'/'),('og:type','article' if kind=='Article' else 'website'),('og:image','https://prep-center.ru/assets/'+image)]:
  old=head.xpath('./meta[@property=$p]',p=prop)
  if old:old[0].set('content',value)
  else:etree.SubElement(head,'meta',property=prop,content=value)
 doc=etree.Element('html',lang='ru');doc.append(head);b=etree.SubElement(doc,'body');b.append(common(header));main=etree.SubElement(b,'main');main.append(article);main.append(common(contact))
 entity={'@context':'https://schema.org','@type':kind,'name':label(article.xpath('.//h1')[0]),'url':'https://prep-center.ru/'+slug+'/'}
 if kind=='Service':entity.update(provider={'@id':'https://prep-center.ru/#organization'},areaServed='Москва и Московская область')
 elif kind=='Article':entity.update(headline=entity['name'],author={'@type':'Organization','name':'Преп-Центр'},datePublished=published,dateModified=modified or published,image='https://prep-center.ru/assets/'+image)
 nodes=[entity,{'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Главная','item':'https://prep-center.ru/'},{'@type':'ListItem','position':2,'name':NAMES[slug],'item':'https://prep-center.ru/'+slug+'/'}]}]
 faq=[{'@type':'Question','name':label(i.xpath('./summary')[0]),'acceptedAnswer':{'@type':'Answer','text':' '.join(label(e) for e in i if e.tag!='summary')}} for i in article.xpath('.//details')]
 if faq:nodes.append({'@context':'https://schema.org','@type':'FAQPage','mainEntity':faq})
 for node in nodes:sc=etree.SubElement(b,'script',type='application/ld+json');sc.text=json.dumps(node,ensure_ascii=False)
 path=SITE/slug/'index.html';path.parent.mkdir(exist_ok=True);path.write_text('<!doctype html>\n'+html.tostring(doc,encoding='unicode',method='html'))
 return {'path':'/'+slug+'/','images':len(article.xpath('.//img')),'faq':len(faq),'kind':kind,'source_published':published,'source_updated':modified}
provenance=[]
for slug in CATEGORIES+['srochnaya-obrabotka-partiy','about']:
 source=html.fromstring((SRC/(slug+'-20260822.html')).read_bytes());a=deepcopy(source.xpath('//article')[0]);css=source.xpath('//main/style')[0].text
 images=a.xpath('.//img')
 maps={
 'about':['about-01-sklad-rabochie-zony.webp','about-02-fasad-sklada.webp','about-03-priemka-razgruzka.webp','about-07-zona-hraneniya.webp','about-04-liniya-termousadki.webp','about-05-tovar-v-vpp.webp','about-06-krupnaya-partiya.webp'],
 'fulfillment-kosmetika':['cos-06.webp','cos-05.webp','cos-01.webp','cos-05.webp','cos-08.webp'],
 'fulfillment-shampuni-geli':['liquid-01.webp','about-05-tovar-v-vpp.webp','about-04-liniya-termousadki.webp','warehouse-worker.webp'],
 'fulfillment-bytovaya-himiya':['household-hero.webp','about-05-tovar-v-vpp.webp','about-04-liniya-termousadki.webp','cos-01.webp'],
 'srochnaya-obrabotka-partiy':['urgent-receipt.webp','about-04-liniya-termousadki.webp','kits-02.webp','stationery-set.webp','about-06-krupnaya-partiya.webp']}
 if slug in maps:
  assert len(images)==len(maps[slug]),slug
  for i,(im,name) in enumerate(zip(images,maps[slug])):image_attrs(im,name,i==0)
 if slug=='fulfillment-bytovaya-himiya':
  im=images[-1];im.set('alt','Приемка и размещение партии товара на складе Преп-Центра')
  for cap in im.getparent().xpath('./figcaption'):cap.text='Приемка и размещение партии товара на складе Преп-Центра'
 if slug in ['fulfillment-avtohimiya','fulfillment-stroitelnaya-himiya']:
  hero=a.xpath('.//*[contains(@class,"__hero")]')[0];addphoto(hero,'about-03-priemka-razgruzka.webp','Приемка товара на складе Преп-Центра')
  sections=a.xpath('.//section');addphoto(sections[3],'about-04-liniya-termousadki.webp','Автоматическая линия термоусадочной упаковки Преп-Центра')
  case=a.xpath('.//*[contains(@class,"__case") and self::section]')[0];addphoto(case,'about-06-krupnaya-partiya.webp' if 'stroitelnaya' in slug else 'bubble-packed-set.webp','Подготовленный товар в защитной упаковке')
 pub='2026-08-21' if slug=='srochnaya-obrabotka-partiy' else '2026-08-22';upd='2026-10-21' if slug=='about' else pub
 h1=a.xpath('.//h1')[0];date=etree.Element('p',{'class':'recovered-date'});date.text=('Опубликовано: 21 августа 2026' if pub.endswith('21') else 'Опубликовано: 22 августа 2026')+(' · Обновлено: 21 октября 2026' if slug=='about' else '')+' · Восстановлено: 4 ноября 2026';h1.addnext(date)
 if slug=='about':
  h=a.xpath('.//h3[normalize-space()="Маркировка и комплектация"]')[0];p=etree.Element('p');p.text='При сборке маркированных наборов связываем КИЗ вложений с кодом набора в WMS МПФИТ и передаем клиенту файл соответствий; для одной упакованной единицы доступно дублирование КИЗ снаружи.';h.addnext(p)
  sec=next(s for s in a.xpath('.//section') if s.xpath('./h2') and label(s.xpath('./h2')[0])=='Оборудование, складской учет и контроль');p=etree.SubElement(sec,'p');p.text='Подробнее: ';etree.SubElement(p,'a',href='/wms-mpfit-dlya-fulfillmenta/').text='как мы используем WMS МПФИТ для учета, маркировки и отгрузок'
 targets=['fulfillment-zhidkih-tovarov','termousadka-vpp','etiketki-marketpleysov','chestnyy-znak','komplektatsiya-naborov','fulfillment-fbo','fulfillment-fbs','srochnaya-obrabotka-partiy','wms-mpfit-dlya-fulfillmenta','contacts']
 if slug=='about':targets=['wms-mpfit-dlya-fulfillmenta','contacts',*CATEGORIES]
 related(a[0],slug,targets)
 (SITE/'assets'/(slug+'.css')).write_text(css)
 result=shell(slug,a,source.xpath('//title')[0].text,source.xpath('//meta[@name="description"]/@content')[0],[slug+'.css'],a.xpath('.//img')[0].get('src').split('/')[-1],'AboutPage' if slug=='about' else 'Service',pub,upd);result.update(complete_source='2026-08-22 HTML',late_index_checked='2026-11-04');provenance.append(result)
def mdpage(slug,meta,body,date,image,targets,published,modified=None):
 parsed=parse(body);intro=[]
 while len(parsed) and parsed[0].tag=='p' and not label(parsed[0]).startswith('[ИЗОБРАЖЕНИЕ'):intro.append(parsed[0]);parsed.remove(parsed[0])
 a=etree.Element('article',{'class':'fboservice marketplace-restored'});c=etree.SubElement(a,'div',{'class':'fboservice__container'});crumb=etree.SubElement(c,'nav',{'class':'fboservice__breadcrumbs','aria-label':'Хлебные крошки'});etree.SubElement(crumb,'a',href='/').text='Главная';etree.SubElement(crumb,'span').text='→ '+NAMES[slug]
 hero=etree.SubElement(c,'section',{'class':'fboservice__hero'});copy=etree.SubElement(hero,'div');etree.SubElement(copy,'p',{'class':'recovered-date'}).text=date+' · Восстановлено: 4 ноября 2026';etree.SubElement(copy,'h1').text=meta['H1']
 for i,p in enumerate(intro):
  if i==0:p.set('class','fboservice__lead')
  copy.append(p)
 hero.append(picture(image,'Складские операции Преп-Центра',True));sec=None;faqmode=False;item=None
 for e in list(parsed):
  if e.tag=='h2':
   sec=etree.SubElement(c,'section',{'class':'fboservice__section'});sec.append(e);faqmode=label(e)=='Частые вопросы'
   if faqmode:sec.set('class','fboservice__section fboservice__faq')
  elif sec is None:continue
  elif faqmode:
   if e.tag=='h3':item=etree.SubElement(sec,'details');etree.SubElement(item,'summary').text=label(e)
   elif item is not None:item.append(e)
  else:sec.append(e)
 if slug=='wms-mpfit-dlya-fulfillmenta':
  for p in list(a.xpath('.//p')):
   m=re.match(r'\[ИЗОБРАЖЕНИЕ (\d\d):',label(p))
   if not m:continue
   nxt=p.getnext();embedded=re.search(r'\]\s*\*([^*]+)\*',label(p));caption=embedded[1] if embedded else label(nxt).strip('*') if nxt is not None and nxt.tag=='p' and label(nxt).startswith('*') else 'WMS МПФИТ: '+m[1]
   fig=etree.Element('figure',{'class':'recovered-photo wms-screenshot'});link=etree.SubElement(fig,'a',href='../assets/wms-'+m[1]+'.webp',target='_blank',rel='noopener',**{'aria-label':'Открыть снимок экрана крупнее: '+caption});im=etree.SubElement(link,'img',alt=caption);image_attrs(im,'wms-'+m[1]+'.webp');etree.SubElement(fig,'figcaption').text=caption
   p.getparent().replace(p,fig)
   if nxt is not None and nxt.tag=='p' and label(nxt).startswith('*'):nxt.getparent().remove(nxt)
 else:
  note=etree.Element('aside',{'class':'fboservice__note'});etree.SubElement(note,'p').text='Требования восстановлены по исходнику от 18.09.2026. Перед поставкой сверяйте действующий регламент и параметры заявки в кабинете ЛЭТУАЛЬ.';hero.addnext(note)
  addphoto(c.xpath('./section')[2],'cos-05.webp','Контроль маркировки косметики на складе Преп-Центра')
 related(c,slug,targets);return shell(slug,a,meta['Title'],meta['Description'],['fulfillment-fbo.css','marketplace-restored.css'],image,'Article',published,modified)
raw=(SRC/'04_info_letual_fbl_cosmetics.md').read_text()
def field(marker):return re.search(r'\[\[AGENT: '+marker+r'\]\]\s*(?:# )?([^\n]+)',raw)[1].strip()
meta={'H1':field('H1'),'Title':field('SEO Title'),'Description':field('Meta Description')};body=re.sub(r'^\s*Проверено:[^\n]*\n','',raw.split('[[AGENT: видимый блок даты]]',1)[1],count=1);body=re.sub(r'\[\[AGENT:.*?\]\]','',body,flags=re.S)
body=re.sub(r'По официальной seller-wiki ЛЭТУАЛЬ, с \*\*1 июля 2026 года\*\*.*?\n\n','Для товаров, подлежащих обязательной маркировке, нужны корректные коды и передача сведений в документах по действующим правилам.\n\n',body,flags=re.S)
provenance.append(mdpage('trebovaniya-fbl-letual',meta,body,'Проверено в исходнике: 18 сентября 2026','cos-08.webp',['fbl-letual','fulfillment-kosmetika','termousadka-vpp','chestnyy-znak','komplektatsiya-naborov'],'2026-09-18'))
raw=(SRC/'wms-source.md').read_text().lstrip('\ufeff');title,body=raw.split('\n',1);body=re.sub(r'\[ИЗОБРАЖЕНИЕ:.*?\]','',body)
delta='''### Дублирование кода одной единицы

На рабочем месте Преп-Центра сотрудник выбирает режим «Дублировать», считывает заводской КИЗ конкретного товара, выполняет согласованную защитную упаковку и печатает этикетку с тем же кодом для внешнего слоя. Оригинальная маркировка остается на товаре.

### Сопоставление кодов при сборке набора

Клиент выпускает и загружает коды готовых наборов и создает заявку с составом. При сборке сотрудник сканирует КИЗ каждого вложения; WMS связывает фактически считанные коды с кодом конкретного набора. Общая этикетка печатается после полного сканирования предусмотренного состава.

Клиент скачивает файл соответствий наборов и вложенных единиц и продолжает оформление в «Честном знаке». Категорию, тип объекта, статусы кодов и формат выгрузки согласовываем до запуска.

'''
body=body.replace('## Разные клиенты — разные правила обработки',delta+'## Разные клиенты — разные правила обработки')
body=body.replace('129 тарифов','134 тарифа')
meta={'H1':title.lstrip('# '),'Title':'WMS МПФИТ в Преп-Центре: как мы управляем фулфилментом | Преп-Центр','Description':'Как Преп-Центр использует WMS МПФИТ для FBO и FBS, единого остатка, КИЗ, адресного хранения, личного кабинета и учета услуг. Реальные снимки экрана и кейсы.'}
provenance.append(mdpage('wms-mpfit-dlya-fulfillmenta',meta,body,'Опубликовано: 5 сентября 2026 · Обновлено: 20 октября 2026','about-01-sklad-rabochie-zony.webp',['about','fulfillment-fbo','fulfillment-fbs','chestnyy-znak','komplektatsiya-naborov','srochnaya-obrabotka-partiy'],'2026-09-05','2026-10-20'))
# The old /contacts/ archive is a banking template. Rebuild from confirmed live company contacts.
a=html.fromstring('''<article class="fboservice"><div class="fboservice__container"><nav class="fboservice__breadcrumbs" aria-label="Хлебные крошки"><a href="/">Главная</a><span>→ Контакты</span></nav><section class="fboservice__hero"><div><p class="recovered-date">Контакты Преп-Центра · Восстановлено: 4 ноября 2026</p><h1>Контакты Преп-Центра</h1><p class="fboservice__lead">Склад в Пушкино. Ежедневно с 08:00 до 20:00.</p><p>Чтобы обсудить партию, уточнить приемку или договориться об экскурсии, свяжитесь с менеджером.</p><div class="fboservice__actions"><a class="fboservice__button" href="tel:+79306007520">Позвонить</a><a class="fboservice__button fboservice__button--ghost" href="https://t.me/prepmanager2">Написать в Telegram</a></div></div></section><section class="fboservice__section contact-cards"><div><h2>Адрес склада</h2><p>Московская область, г. Пушкино, ул. Новая, д. 10</p><p>Ежедневно с 08:00 до 20:00</p><p>Перед приездом согласуйте время и состав партии с менеджером.</p></div><div><h2>Связаться с нами</h2><p><a href="tel:+79306007520">+7 (930) 600 75 20</a></p><p><a href="mailto:info@prep-center.ru">info@prep-center.ru</a></p><p><a href="https://t.me/prepmanager2">Telegram: @prepmanager2</a></p></div></section><section class="fboservice__section"><h2>Что прислать для расчета</h2><p>Фотографии товара, количество единиц и SKU, размеры упаковки, список необходимых операций, маркетплейс и планируемую дату поставки.</p><p>Менеджер подтвердит возможность приемки, срок обработки и стоимость.</p><a class="fboservice__button" href="https://t.me/prepmanager2">Обсудить партию</a></section></div></article>''')
a.xpath('.//section')[0].append(picture('about-02-fasad-sklada.webp','Фасад склада Преп-Центра в Пушкино',True));related(a[0],'contacts',['about','wms-mpfit-dlya-fulfillmenta','fulfillment-fbo','fulfillment-fbs','srochnaya-obrabotka-partiy'])
provenance.append(shell('contacts',a,'Контакты Преп-Центра: склад в Пушкино, телефон и Telegram','Контакты Преп-Центра: +7 (930) 600 75 20, info@prep-center.ru, Telegram @prepmanager2. Склад: Пушкино, ул. Новая, 10. Ежедневно 08:00–20:00.',['fulfillment-fbo.css','marketplace-restored.css'],'about-02-fasad-sklada.webp','ContactPage'))
# Refresh shared components and activate stored original destinations everywhere.
for p in SITE.glob('*/index.html'):
 slug=p.parent.name;d=html.fromstring(p.read_bytes());article=d.xpath('//main/article')[0];resolve_links(article)
 if slug not in NEW:
  targets=[]
  if slug in ['fulfillment-zhidkih-tovarov','fulfillment-fbo','fulfillment-fbs']:targets=CATEGORIES+['srochnaya-obrabotka-partiy','wms-mpfit-dlya-fulfillmenta']
  elif slug=='fbl-letual':targets=['trebovaniya-fbl-letual','fulfillment-kosmetika','chestnyy-znak']
  elif slug in ['termousadka-vpp','etiketki-marketpleysov','chestnyy-znak','komplektatsiya-naborov']:targets=CATEGORIES+['wms-mpfit-dlya-fulfillmenta','srochnaya-obrabotka-partiy']
  if targets:related(article[0],slug,targets)
 for selector,new in [('//header',common(header)),('//*[@id="contact"]',common(contact))]:
  old=d.xpath(selector)[0];old.getparent().replace(old,new)
 if not d.xpath('//link[contains(@href,"second-recovery.css")]'):etree.SubElement(d.xpath('//head')[0],'link',rel='stylesheet',href='../assets/second-recovery.css')
 p.write_text('<!doctype html>\n'+html.tostring(d,encoding='unicode',method='html'))
(SRC/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2));print(json.dumps(provenance,ensure_ascii=False))
