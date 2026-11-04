from pathlib import Path
from urllib.parse import urlsplit
import csv,io,re,json
from collections import Counter

R=Path(__file__).parent;S=R/'source';rows={}
for row in csv.reader(io.StringIO((S/'pages-index-20260822.csv').read_text().split('\f')[0])):
    if len(row)<10 or not row[1].isdigit():continue
    path=urlsplit(row[3]).path or '/'
    r=rows.setdefault(path,{'path':path,'title':row[9] or row[8],'sources':[],'latest_capture':'','status':'Ожидает восстановления'})
    if 'Drive 22.08.2026' not in r['sources']:r['sources'].append('Drive 22.08.2026')
    r['latest_capture']='22.08.2026: каталог полного HTML и двух скриншотов'
    r['source_folder']=row[2]
text=(S/'all-search-evidence.txt').read_text()
# Result headings and failed source fetches both prove an observed URL. Only
# complete text extractions are marked as content available.
for section in text.split('--------------------------------------------------------------------------------'):
    urls=re.findall(r'https://prep-center\.ru(?:/[^\s\)\]"<>]*)?',section)
    if not urls:continue
    first=urls[0].rstrip('.,;:')
    path=urlsplit(first).path or '/'
    if path.endswith('/'):path=path
    title=section.strip().split('\n')[0].split(' (https://')[0]
    if title.startswith(('Failed','Internal','【')):title=path
    r=rows.setdefault(path,{'path':path,'title':title,'sources':[],'latest_capture':'','status':'Ожидает восстановления'})
    if 'Поисковый индекс, проверка 04.11.2026' not in r['sources']:r['sources'].append('Поисковый индекс, проверка 04.11.2026')
    crawl=re.search(r'Crawled: ([^;\n]+)',section)
    if crawl:r['latest_capture']='Обход: '+crawl[1]+'; точная дата снимка не раскрыта'
    if 'Total lines:' in section and '\nL' in section:r['indexed_text_available']=True
    if r['title']==path and title!=path:r['title']=title

# URLs found in the later cached navigation, or independent site result pages.
additional={
'/tarify/':'Тарифы на фулфилмент',
'/fbo-wildberries/':'Подготовка поставок Wildberries FBW',
'/fbo-ozon/':'Подготовка поставок FBO Ozon',
'/fby-yandex-market/':'Подготовка поставок FBY Яндекс Маркет',
'/fbl-letual/':'Подготовка поставок FBL ЛЭТУАЛЬ',
'/fbs-wildberries/':'FBS для Wildberries',
'/fbs-ozon/':'FBS для Ozon',
'/fbs-yandex-market/':'FBS для Яндекс Маркета',
'/trebovaniya-fbw-wildberries/':'Требования Wildberries FBW',
'/trebovaniya-fbo-ozon/':'Требования Ozon FBO',
'/trebovaniya-fby-yandex-market/':'Требования Яндекс Маркета FBY',
'/trebovaniya-fbl-letual/':'Требования ЛЭТУАЛЬ FBL',
'/trebovaniya-fbs-wildberries/':'Требования Wildberries FBS',
'/trebovaniya-fbs-ozon/':'Требования Ozon FBS',
'/trebovaniya-fbs-yandex-market/':'Требования Яндекс Маркета FBS',
'/wms-mpfit-dlya-fulfillmenta/':'WMS МПФИТ в Преп-Центре',
'/online/':'Преп-Центр в интернете',
'/agregatsiya-kiz-naborov/':'Агрегация КИЗ наборов',
'/cases/agregatsiya-kiz-naborov-wms/':'Агрегация КИЗ набора через WMS: кейс',
'/cases/avtomatizirovannaya-upakovka-kosmetiki/':'Автоматизированная упаковка косметики: кейс',
}
for path,title in additional.items():
    r=rows.setdefault(path,{'path':path,'title':title,'sources':['Поисковый индекс / осеннее меню, проверка 04.11.2026'],'latest_capture':'Осенняя версия; точная дата снимка не подтверждена','status':'Ожидает восстановления'})
    if r['title']==path:r['title']=title

for path,r in rows.items():
    if path.startswith('/services/'):
        r['group']='Остатки банковского шаблона';r['status']='Исключено из восстановления'
    elif path in ['/404.php','/auth.php','/search/','/search/map.php','/thanks/','/spasibo']:
        r['group']='Служебные URL';r['status']='Отдельное решение при восстановлении функций'
    elif path.startswith(('/about/history','/about/management','/about/mission','/about/vacancies','/contacts/feedback','/contacts/requisites')) or path=='/news/':
        r['group']='Старые разделы: требуется проверка содержания';r['status']='Не подтверждено актуальное содержание'
    elif path.startswith('/cases/') and path!='/cases/':r['group']='Кейсы'
    elif path.startswith('/trebovaniya-') or path in ['/blog/','/upakovka-bytovoy-khimii/','/wms-mpfit-dlya-fulfillmenta/']:r['group']='Статьи и требования маркетплейсов'
    elif path=='/':r['group']='Основные страницы';r['status']='Восстановленная временная главная опубликована'
    elif path in ['/about/','/online/','/contacts/','/privacy-policy/','/cases/','/tarify/']:r['group']='Основные страницы'
    else:r['group']='Услуги и категории'
    if path=='/fulfillment-zhidkih-tovarov/':
        r['status']='Сверстана и опубликована первая внутренняя страница; проверка отображения отмечена в журнале'
        r['latest_capture']='Индекс: 2 weeks ago (проверка 04.11.2026); HTML и скриншоты 22.08.2026; текст сопоставлен'
        r['assets']='6 исходных изображений найдены и добавлены'

allrows=sorted(rows.values(),key=lambda r:(r['group'],r['path']))
public=[r for r in allrows if r['group'] not in ['Остатки банковского шаблона','Служебные URL','Старые разделы: требуется проверка содержания']]
fields=['path','title','group','latest_capture','status','sources','assets']
with (R/'page-inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
    for r in allrows:w.writerow({**r,'sources':'; '.join(r['sources'])})
(R/'page-inventory.json').write_text(json.dumps(allrows,ensure_ascii=False,indent=2))
counts=Counter(r['group'] for r in allrows)
lines=['# Опись восстановления prep-center.ru','',
'Составлена 4 ноября 2026 года. Это подтвержденный на текущем проходе список, а не утверждение, что найдены абсолютно все страницы. Якоря главной (отзывы, FAQ, калькулятор, контакты) не считались отдельными страницами. HTTP/HTTPS главной объединены.','',
f'Найдено {len(allrows)} уникальных путей: {len(public)} содержательных страниц в основной очереди; остальные разделены на старые разделы, служебные адреса и остатки банковского шаблона.','',
'## Источники и свежесть','',
'- Поисковый индекс сайта: содержимое и меню, прочитанные 04.11.2026. Есть страницы с обходом «2 недели назад», «на прошлой неделе» и «2 дня назад». Эти относительные отметки не заменены выдуманными точными датами.','- Сохраненный полный снимок от 22.08.2026: каталог 55 исходных URL, HTML и скриншоты. Используется как запасной источник структуры и изображений, а не как доказательство октябрьского состояния.','- Wayback CDX: на этом проходе вернул только главную, политику и старый адрес благодарности. Свежих октябрьских внутренних страниц через этот ответ не получено. Июньская главная не использовалась как основа новых страниц.','- Осенние страницы по FBO/FBS, требованиям, WMS и агрегации сверены с поиском. Тексты тарифов из индекса могут отставать от согласованных изменений 20.10.2026; прайс требует отдельного сопоставления.','',
'## Основная очередь','',
'| № | Страница | Старый путь | Найденные материалы / состояние |','|---|---|---|---|']
for i,r in enumerate(public,1):
    material='HTML и скриншоты в снимке 22.08.2026' if 'source_folder' in r else 'URL и следы в осеннем поисковом индексе / меню'
    if r.get('indexed_text_available'):material+='; извлечен текст из индекса'
    if r['path']=='/fulfillment-zhidkih-tovarov/':material+='; 6 изображений; первая сверстанная внутренняя страница'
    lines.append(f'| {i} | {r["title"].replace("|","/")} | `{r["path"]}` | {material} |')
for group in ['Старые разделы: требуется проверка содержания','Служебные URL','Остатки банковского шаблона']:
    lines+=['',f'## {group}','', '| Путь | Название | Решение |','|---|---|---|']
    for r in allrows:
        if r['group']==group:lines.append(f'| `{r["path"]}` | {r["title"].replace("|","/")} | {r["status"]} |')
lines+=['','## Первая страница','',
'`/fulfillment-zhidkih-tovarov/`: восстановлены оригинальные разделы и компонентные стили, все 6 исходных изображений, таблица цен и 9 раскрывающихся ответов. Основной текст сопоставлен с поздней индексной копией. Сохранены исходный HTML и сведения о происхождении.','',
'Ограничения: серверная отправка заявок пока не восстановлена; вместо нее доступны контакты и Telegram. Ссылки на еще не восстановленные разделы временно ведут на главную; оригинальные цели сохранены в data-original-href. Запрет индексации временного сайта сохранен до отдельной проверки запуска на основном домене.','',
'## Порядок следующих работ','',
'1. Тарифы: восстановить актуальные 134 позиции и отдельно сверить изменения 20.10.2026.','2. FBO/FBS и требования четырех маркетплейсов, категории товаров.','3. Кейсы, WMS, агрегация КИЗ, комплектация наборов.','4. Каталоги статей и кейсов, страница компании, внешние профили, политика.','5. Общие меню, формы, калькулятор, аналитика и цели после выбора рабочей серверной отправки. Не считать старый Bitrix восстановленным на статическом хостинге.','']
(R/'PAGE_INVENTORY.md').write_text('\n'.join(lines))
print(json.dumps({'all_paths':len(allrows),'main_queue':len(public),'groups':dict(counts)},ensure_ascii=False))
