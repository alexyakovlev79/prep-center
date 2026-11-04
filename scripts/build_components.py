"""Render canonical shared components into static pages; no browser-side includes."""
from pathlib import Path
from html import escape as e
import json,re,sys
ROOT=Path(__file__).resolve().parent.parent
NAV=json.loads((ROOT/'components/navigation.json').read_text())
def link(item):return '<a href="'+e(item['href'],quote=True)+'">'+e(item['label'])+'</a>'
def render(items,depth=0):
 result=[]
 for item in items:
  if item.get('children'):
   labels={'Услуги':'Все услуги','Фулфилмент':'Все направления','Кейсы':'Все кейсы','Статьи':'Все статьи','FBO-поставки':'Все FBO-поставки','FBS-отгрузки':'Все FBS-отгрузки'}
   first='' if any(x['href']==item['href'] for x in item['children']) else '<li>'+link(dict(item,label=labels.get(item['label'],item['label'])))+'</li>'
   content=first+render(item['children'],depth+1)
   result.append('<li><details class="nav-group"><summary>'+e(item['label'])+'</summary><ul>'+content+'</ul></details></li>')
  else:result.append('<li>'+link(item)+'</li>')
 return ''.join(result)
menu='<ul class="nav-root">'+render(NAV)+'</ul>'
header=(ROOT/'components/header.html').read_text().replace('{{BURGER_NAV}}',menu).replace('{{DESKTOP_NAV}}',menu).strip()
info=[dict(label='Тарифы',href='/tarify/'),dict(label='Кейсы',href='/cases/'),dict(label='Статьи',href='/blog/'),dict(label='О компании',href='/about/'),dict(label='Преп-Центр в интернете',href='/online/'),dict(label='Отзывы',href='/#reviews'),dict(label='Вопросы и ответы',href='/#questions'),dict(label='Контакты',href='/contacts/')]
fnav=''.join('<nav aria-label="'+label+' в подвале"><h3>'+label+'</h3><ul>'+''.join('<li>'+link(x)+'</li>' for x in items)+'</ul></nav>' for label,items in [('Услуги',NAV[0]['children']),('Фулфилмент',NAV[1]['children']),('Информация',info)])
footer=(ROOT/'components/footer.html').read_text().replace('{{FOOTER_NAV}}',fnav).strip()
inv=json.loads((ROOT/'restoration/page-inventory.json').read_text())
routes=[x['path'] for x in inv if x.get('group') in {'Услуги и категории','Статьи и требования маркетплейсов','Кейсы','Основные страницы'}]
changed=[]
for route in routes:
 p=ROOT/route.strip('/')/'index.html';old=p.read_text();s=old
 s=re.sub(r'<header\b.*?</header>\s*',lambda m:header,s,count=1,flags=re.S)
 s=re.sub(r'<section class="contact section-dark(?: shared-contact)?" id="contact">.*?</section>\s*',lambda m:footer,s,count=1,flags=re.S)
 s=re.sub(r'<link rel="stylesheet" href="/assets/shared-components.css(?:\?[^\"]*)?">','',s)
 s=s.replace('</head>','<link rel="stylesheet" href="/assets/shared-components.css?v=20261104"></head>')
 s=re.sub(r'<script defer src="/assets/shared-components.js(?:\?[^\"]*)?"></script>','',s)
 s=s.replace('</body>','<script defer src="/assets/shared-components.js?v=20261104"></script></body>')
 # Restore review destinations whose original targets were disabled in emergency recovery.
 s=re.sub(r'(<a\b[^>]*href=")/("[^>]*>Смотреть отзыв в Яндекс)',r'\1https://yandex.ru/maps/org/prep_tsentr/113144699853/reviews/\2',s)
 s=re.sub(r'(<a\b[^>]*href=")/("[^>]*>Показать все отзывы)',r'\1https://yandex.ru/maps/org/prep_tsentr/113144699853/reviews/\2',s)
 s=re.sub(r'(<a\b[^>]*href=")/("[^>]*>Посмотреть все 134 тарифа)',r'\1/tarify/\2',s)
 # All map/review outbound links open separately.
 s=re.sub(r'<a\b[^>]*href="https://yandex.ru/maps/[^\"]*"[^>]*>',lambda m:re.sub(r'\s(?:target|rel)="[^"]*"','',m[0])[:-1]+' target="_blank" rel="noopener">',s)
 if old!=s:
  changed.append(str(p.relative_to(ROOT)))
  if '--check' not in sys.argv:p.write_text(s)
if '--check' in sys.argv and changed:raise SystemExit('Stale generated components: '+', '.join(changed))
print(('Checked' if '--check' in sys.argv else 'Updated'),len(routes),'pages;',len(changed),'changed')
