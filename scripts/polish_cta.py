"""Canonical CTA normalization. Rewrites only CTA elements, not article text/layout.
Run after build_components.py. Archived restoration sources are never modified.
"""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
from urllib.parse import quote, urlsplit
import re,json
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
VERSION='20261110-cta-v1'
TG='https://t.me/prepmanager2'
DARK={'hero','shared-contact','section-dark','online-cta-box','marketplace-final-actions','fboservice__cta','fbsservice__cta','aboutpage__cta','kitservice__cta','liquidservice__final','czservice__final','packservice__final','labelsservice__final','urgservice__final','service-page__cta','coscase__cta','autocase__cta','chemcase__cta','kitcase__cta','processcase__cta','autservice__case','cosservice__case','chemservice__case','prep-article-cta__box'}
TOPICS={
'':'подготовку товаров к маркетплейсам',
'about':'сотрудничество с Преп-Центром',
'online':'условия работы и услуги Преп-Центра',
'contacts':'сотрудничество с Преп-Центром',
'tarify':'стоимость обработки моей партии товаров',
'blog':'подготовку моей партии товаров к маркетплейсам',
'cases':'похожую задачу по подготовке товаров к маркетплейсам',
'wms-mpfit-dlya-fulfillmenta':'складской учет, остатки и работу через личный кабинет МПФИТ в Преп-Центре',
'upakovka-bytovoy-khimii':'упаковку бытовой химии под мой продукт',
'fulfillment-bytovaya-himiya':'фулфилмент партии бытовой химии',
'fulfillment-shampuni-geli':'упаковку и фулфилмент шампуней и гелей',
'fulfillment-kosmetika':'упаковку и подготовку косметики для Wildberries и Ozon',
'fulfillment-avtohimiya':'подготовку автохимии и автокосметики',
'fulfillment-stroitelnaya-himiya':'подготовку партии строительной химии',
'fulfillment-zhidkih-tovarov':'упаковку и фулфилмент жидких товаров',
'fulfillment-fbo':'подготовку FBO-поставки на склад маркетплейса',
'fulfillment-fbs':'хранение, сборку и отгрузку FBS-заказов',
'komplektatsiya-naborov':'комплектацию и сборку товарных наборов',
'termousadka-vpp':'упаковку товаров в термоусадку и ВПП',
'chestnyy-znak':'маркировку партии кодами Честного знака',
'etiketki-marketpleysov':'печать и наклейку этикеток маркетплейсов',
'agregatsiya-kiz-naborov':'агрегацию КИЗ при сборке маркированных наборов',
'srochnaya-obrabotka-partiy':'срок и стоимость срочной обработки крупной партии',
'cases/kosmetika-8400-za-2-dnya':'похожую задачу: упаковку и маркировку партии косметики для Wildberries и Ozon',
'cases/avtohimiya-2393-nabora-za-2-dnya':'похожую задачу: сборку подарочных наборов автохимии',
'cases/stroitelnaya-himiya-5180-za-3-dnya':'похожую задачу: упаковку строительной химии в термоусадку и ВПП',
'cases/kantselyarskie-nabory-6000-za-5-dney':'похожую задачу: комплектацию подарочных канцелярских наборов',
'cases/opolaskivateli-3186-za-2-dnya':'похожую задачу: упаковку ополаскивателей и других жидких товаров в ВПП',
'cases/agregatsiya-kiz-naborov-wms':'сборку маркированных наборов и агрегацию КИЗ через WMS',
'cases/avtomatizirovannaya-upakovka-kosmetiki':'автоматизированную упаковку партии косметики',
}
for key,topic in {'fbl-letual':'подготовку косметики и парфюмерии к FBL-поставке в ЛЭТУАЛЬ','fbo-ozon':'подготовку FBO-поставки на Ozon','fbo-wildberries':'подготовку FBW-поставки на Wildberries','fby-yandex-market':'подготовку FBY-поставки на Яндекс Маркет','fbs-ozon':'FBS-фулфилмент для Ozon','fbs-wildberries':'FBS-фулфилмент для Wildberries','fbs-yandex-market':'FBS-фулфилмент для Яндекс Маркета'}.items():
 TOPICS[key]=topic
 TOPICS['trebovaniya-'+key.replace('fbo-wildberries','fbw-wildberries')]=topic+' по требованиям площадки'
class Bounds(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=False);self.text=text;self.lines=[0];self.stack=[];self.spans={}
  for m in re.finditer('\n',text):self.lines.append(m.end())
  self.feed(text)
 def pos(self):
  line,col=self.getpos();return self.lines[line-1]+col
 def handle_starttag(self,tag,attrs):
  at=self.pos()
  if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append((tag,at))
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i][0]==tag:
    _,start=self.stack[i];self.spans[start]=(start,self.text.index('>',self.pos())+1);del self.stack[i:];return
 def span(self,tag):
  start=self.lines[tag.sourceline-1]+tag.sourcepos
  return self.spans[start]
def classes(tag):return set(tag.get('class',[]))
def text(tag):return re.sub(r'\s+',' ',tag.get_text(' ',strip=True)).strip()
def dark(tag):return any(classes(n)&DARK for n in tag.parents if n.name)
def heading(tag):
 for par in tag.parents:
  if par.name in {'body','html','main'}:break
  h=par.find(['h2','h3','h4'])
  if h:return text(h)
 return ''
def request(route,tag):
 if tag.find_parent('header'):return ''
 if tag.find_parent(class_='shared-contact'):return 'Хочу записаться на экскурсию на склад Преп-Центра.'
 h=heading(tag).lower();label=text(tag).lower()
 if 'экскурс' in label or ('about'==route and ('посмотреть склад' in h or 'приезжайте' in h)):
  return 'Хочу записаться на экскурсию на склад Преп-Центра.'
 topic=TOPICS.get(route,'подготовку моей партии товаров к маркетплейсам')
 if 'доставк' in h and 'fulfillment-fbo'==route:return 'Хочу обсудить доставку подготовленной FBO-поставки на склад маркетплейса.'
 if 'крупн' in h and route=='fulfillment-fbo':return 'Хочу обсудить срочную подготовку крупной FBO-поставки.'
 if route=='termousadka-vpp' and 'сто' in h:return 'Прошу рассчитать стоимость упаковки моей партии в термоусадку и ВПП.'
 return 'Хочу обсудить '+topic+'.'
def eligible(a):
 return 'pc-action' in classes(a) or bool(re.search(r'button|btn|cta',' '.join(a.get('class',[])),re.I)) or (a.find_parent('header') and text(a)=='Обсудить задачу')
def kind(a,route):
 href=a.get('href','');label=text(a)
 if a.get('id')=='calc-telegram':return 'telegram'
 if a.get('id')=='calc-send-form':return 'form'
 if a.find_parent(id='calc'):return 'step'
 if a.find_parent('header') and label=='Обсудить задачу':return 'form'
 if label in {'Начать сотрудничество','Записаться на экскурсию'}:return 'form'
 if '#modal' in href or '#prep-article-form' in href or a.get('data-prep-request') is not None and 'pc-action--form' in classes(a):return 'form'
 if href.startswith('https://t.me/'):return 'telegram'
 if href.startswith('tel:'):return 'form' if route=='contacts' and eligible(a) else 'nav'
 if '#calc' in href:return 'calc' if route in {'','tarify'} else 'form'
 if route.startswith('cases/') and any('__callout' in c for c in a.parent.get('class',[])) and href.startswith('/fulfillment-'):return 'form'
 return 'nav'
def decorate(a,k,route,msg=None):
 a=BeautifulSoup(str(a),'html.parser').find(a.name)
 oldhref=a.get('href','');label=text(a)
 a['class']=list(dict.fromkeys([c for c in a.get('class',[]) if not c.startswith('pc-action--')]+['pc-action','pc-action--'+k]))
 a['data-cta-tone']='dark' if a.get('data-cta-tone')=='dark' else 'light'
 if k=='form' and a.get('id')!='calc-send-form':
  a['href']='#modal';a['aria-haspopup']='dialog';a['data-prep-request']=msg or ''
  for attr in ['target','rel','data-original-href']:a.attrs.pop(attr,None)
  if oldhref.startswith('/fulfillment-') and route.startswith('cases/'):
   a.clear();a.append('Обсудить похожую задачу')
  elif oldhref.startswith('tel:'):a.clear();a.append('Связаться с нами')
  elif '#calc' in oldhref:a.clear();a.append('Получить расчет')
  if msg and 'экскурси' in msg:a['data-prep-intent']='excursion'
 if k=='telegram' and a.get('id')!='calc-telegram':
  a['href']=TG+('?text='+quote(msg,safe='') if msg else '');a['target']='_blank';a['rel']=['noopener'];a['data-prep-request']=msg or ''
 if k=='nav':
  a.attrs.pop('data-prep-request',None)
 return a
def pair_markup(route,a,msg,tone):
 f=BeautifulSoup('<a href="#modal">Обсудить задачу</a>','html.parser').a
 if 'экскурси' in msg:f.string='Записаться на экскурсию'
 t=BeautifulSoup('<a>Написать в Telegram</a>','html.parser').a
 f=decorate(f,'form',route,msg);t=decorate(t,'telegram',route,msg)
 f['data-cta-tone']=tone;t['data-cta-tone']=tone
 return str(f)+str(t)
def normalize(original,route,component=False):
 soup=BeautifulSoup(original,'html.parser');bounds=Bounds(original);changes=[];groups={};done=set();body_conversions=0
 for a in soup.find_all('a'):
  if not eligible(a):continue
  k=kind(a,route)
  if a.find_parent('header'):
   msg='';n=decorate(a,k,route,msg);n['data-cta-tone']='dark';start,end=bounds.span(a);changes.append((start,end,str(n)));continue
  if a.find_parent(id='calc'):
   n=decorate(a,k,route);n['data-cta-tone']='light';start,end=bounds.span(a);changes.append((start,end,str(n)));continue
  par=a.parent
  direct=par.find_all('a',recursive=False)
  dedicated=('pc-actions' in classes(par) or bool(re.search(r'actions|__links',' '.join(par.get('class',[])))))
  members=[x for x in direct if eligible(x)] if dedicated else [a]
  key=tuple(bounds.span(x)[0] for x in members)
  if key in done:continue
  done.add(key)
  data=[]
  for x in members:
   typ=kind(x,route);msg=x.get('data-prep-request') if x.has_attr('data-prep-request') else request(route,x)
   n=decorate(x,typ,route,msg);tone='dark' if dark(x) else 'light';n['data-cta-tone']=tone
   data.append((n,typ,msg))
   if typ in {'form','telegram'} and not x.find_parent(class_='shared-contact'):body_conversions+=1
  types=[x[1] for x in data]
  if 'form' in types and 'telegram' not in types:
   n=BeautifulSoup('<a>Написать в Telegram</a>','html.parser').a
   msg=next(x[2] for x in data if x[1]=='form');n=decorate(n,'telegram',route,msg);n['data-cta-tone']=data[0][0]['data-cta-tone']
   idx=next(i for i,x in enumerate(data) if x[1]=='form')+1;data.insert(idx,(n,'telegram',msg))
  elif 'telegram' in types and 'form' not in types:
   msg=data[0][2];n=BeautifulSoup('<a>Связаться с нами</a>','html.parser').a;n=decorate(n,'form',route,msg);n['data-cta-tone']=data[0][0]['data-cta-tone'];data.insert(0,(n,'form',msg))
  content=''.join(str(x[0]) for x in data)
  start=bounds.span(members[0])[0];end=bounds.span(members[-1])[1]
  if 'pc-actions' in classes(par):repl=content
  elif any(x[1] in {'form','telegram'} for x in data):repl='<span class="pc-actions">'+content+'</span>'
  else:repl=content
  changes.append((start,end,repl))
 for b in soup.find_all('button'):
  if not eligible(b) or b.find_parent('form') and not b.find_parent(id='calc'):continue
  typ='step' if b.find_parent(id='calc') else 'nav'
  if b.get('id')=='calc-send-form':typ='form'
  n=decorate(b,typ,route);start,end=bounds.span(b);changes.append((start,end,str(n)))
 if not component and not body_conversions and route!='privacy-policy' and not soup.select('.pc-page-contact'):
  footer=soup.find('section',id='contact')
  if footer:
   msg='Хочу обсудить '+TOPICS.get(route,'подготовку моей партии товаров к маркетплейсам')+'.'
   last=soup.find('main');sections=[x for x in last.find_all('section') if not x.find_parent(class_='shared-contact') and 'shared-contact' not in classes(x)] if last else []
   target=next((x for x in reversed(sections) if x.find(['h2','h3']) and re.search(r'Рассчитать|Нужно|Что нужно для расчета',text(x.find(['h2','h3'])))),None)
   pair='<span class="pc-actions">'+pair_markup(route,None,msg,'light')+'</span>'
   if target and not target.select('.pc-actions'):
    at=bounds.span(target)[1]-len('</section>');changes.append((at,at,pair))
   else:
    title='Обсудим вашу задачу?' if route not in {'tarify','cases'} else ('Рассчитаем вашу партию' if route=='tarify' else 'У вас похожая задача?')
    extra=str(BeautifulSoup('<a class="pc-action pc-action--calc" data-cta-tone="light" href="/#calc">Калькулятор стоимости</a>','html.parser').a) if route=='tarify' else ''
    if extra:pair=pair.replace('</span>',extra+'</span>')
    block='<section class="pc-page-contact"><div class="container"><h2>'+title+'</h2><p>Расскажите о товаре и объеме партии. Подберем операции и обсудим сроки.</p>'+pair+'</div></section>'
    at=bounds.span(footer)[0];changes.append((at,at,block))
 for el in soup.select('[data-prep-inline-form]'):
  if route and not el.has_attr('data-prep-request'):
   at=bounds.span(el)[0];end=original.index('>',at)+1;old=original[at:end]
   changes.append((at,end,old[:-1]+' data-prep-request="'+escape('Хочу обсудить '+TOPICS.get(route,'подготовку товаров')+'.',quote=True)+'">'))
 changes.sort(key=lambda x:(x[0],x[1]));last=-1
 for st,en,_ in changes:
  if st<last:raise RuntimeError('Overlapping CTA edits: '+route)
  last=en
 s=original
 for st,en,new in reversed(changes):s=s[:st]+new+s[en:]
 if not component:
  s=re.sub(r'<link[^>]*href="/assets/cta\.css[^\"]*"[^>]*>','',s)
  s=s.replace('</head>','<link rel="stylesheet" href="/assets/cta.css?v='+VERSION+'"></head>')
  s=re.sub(r'(/assets/shared-components\.js)(?:\?[^\"]*)?',r'\1?v='+VERSION,s)
 return s

def run():
 changed=[];pages=[]
 for p in sorted(ROOT.rglob('index.html')):
  rel=p.relative_to(ROOT)
  if {'restoration','tools','components','serverless','.git','node_modules'}&set(rel.parts):continue
  route=str(rel.parent);route='' if route=='.' else route
  old=p.read_text();new=normalize(old,route)
  if old!=new:p.write_text(new);changed.append(str(rel))
  s=BeautifulSoup(new,'html.parser');pages.append({'path':str(rel),'actions':[{'text':text(a),'href':a.get('href'),'kind':next((c[11:] for c in classes(a) if c.startswith('pc-action--')),''),'request':a.get('data-prep-request',''),'tone':a.get('data-cta-tone','')} for a in s.select('.pc-action')]})
 for name in ['header','footer']:
  p=ROOT/'components'/f'{name}.html';old=p.read_text();new=normalize(old,'',True)
  if new!=old:p.write_text(new);changed.append(str(p.relative_to(ROOT)))
 nav=ROOT/'components/navigation.json';data=json.loads(nav.read_text());data[-1]['href']='#modal';nav.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 head=ROOT/'components/head.html';s=head.read_text()
 if '/assets/cta.css' not in s:head.write_text(s.rstrip()+'\n<link rel="stylesheet" href="/assets/cta.css?v='+VERSION+'">\n')
 report=ROOT/'reports/cta-audit.json';report.parent.mkdir(exist_ok=True);report.write_text(json.dumps(pages,ensure_ascii=False,indent=2)+'\n')
 print('CTA_PAGES',len(pages),'CHANGED',len(changed),'ACTIONS',sum(len(p['actions']) for p in pages))
if __name__=='__main__':run()
