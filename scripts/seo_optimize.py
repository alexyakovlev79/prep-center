#!/usr/bin/env python3
"""Targeted on-page SEO improvements for Prep-Center's 45 canonical pages.

Edits ONLY selected weak/misaligned metadata and a few headings. Does not
rewrite unrelated content, prices, FAQ, navigational URLs or historical files.
The semantic groups below are intent hypotheses, NOT Wordstat frequency data.
"""
from __future__ import annotations

from datetime import datetime, timezone, date
from pathlib import Path
from html import escape, unescape
from collections import defaultdict
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
BASE="https://prep-center.ru"
GROUPS={"Услуги и категории","Статьи и требования маркетплейсов","Кейсы","Основные страницы"}
# title, description, optional visible H1, target query cluster, intent.
# Every factual claim below appears on its corresponding current page.
SEO={
"/": (
"Фулфилмент для маркетплейсов в Москве: FBO, FBS, цены | Преп-Центр",
"Фулфилмент для Wildberries, Ozon и Яндекс Маркета в Москве и МО: приемка, упаковка, маркировка, FBO и FBS. Склад 1560 м² в Пушкино, 134 тарифа.",
None, "фулфилмент для маркетплейсов Москва; фулфилмент Wildberries Ozon; цены FBO FBS", "commercial-general"),
"/tarify/": (
"Цены на фулфилмент и упаковку товаров для маркетплейсов | Преп-Центр",
"134 тарифа Преп-Центра: приемка, маркировка, упаковка в ВПП и термоусадку, хранение, комплектация, FBO, FBS и доставка товаров на Wildberries и Ozon.",
None, "фулфилмент цены; стоимость упаковки товаров; услуги фулфилмента прайс", "commercial-pricing"),
"/fulfillment-fbo/": (
"Фулфилмент FBO для Wildberries, Ozon и Яндекс Маркета | Преп-Центр",
"FBO-фулфилмент в Москве и МО: приемка товаров, упаковка, этикетки, Честный знак, короба и паллеты. Подготовка поставок для Ozon, Wildberries и Яндекс Маркета.",
None, "фулфилмент FBO; подготовка FBO поставок; FBO Москва", "commercial-fbo"),
"/fulfillment-fbs/": (
"Фулфилмент FBS для Wildberries, Ozon и Яндекс Маркета | Преп-Центр",
"Фулфилмент FBS в Москве и МО: хранение, сборка и упаковка заказов, маркировка, учет остатков через WMS и регулярные отгрузки для Wildberries, Ozon и Яндекс Маркета.",
None, "фулфилмент FBS; склад FBS Wildberries Ozon; сборка FBS заказов", "commercial-fbs"),
"/fbo-ozon/": (
"Подготовка поставок FBO Ozon: упаковка и доставка | Преп-Центр",
"Подготовим поставку FBO на склады Ozon: приемка, сортировка, упаковка, этикетки, Честный знак, формирование коробов и паллет. Доставка по графику, склад в Пушкино.",
None, "подготовка поставок Ozon FBO; упаковка товаров Озон; отгрузка FBO", "commercial-marketplace-fbo"),
"/fbo-wildberries/": (
"Подготовка поставок Wildberries FBW (FBO): упаковка | Преп-Центр",
"Подготовка поставок на склад Wildberries (FBW/FBO): приемка, проверка, упаковка товара, маркировка, короба и паллеты. Склад в Пушкино, доставка по графику.",
None, "подготовка поставок Wildberries; упаковка товаров для ВБ; FBW FBO", "commercial-marketplace-fbo"),
"/fby-yandex-market/": (
"Подготовка поставок FBY Яндекс Маркета: упаковка | Преп-Центр",
"Подготовка FBY-поставок на Яндекс Маркет: проверка товара, упаковка, этикетки, формирование коробов и паллет. Работа с маркировкой и транспортными грузоместами.",
None, "поставки FBY Яндекс Маркет; подготовка товаров на склад Яндекс Маркета", "commercial-marketplace-fbo"),
"/fbs-ozon/": (
"Фулфилмент FBS Ozon: хранение, сборка, отгрузка | Преп-Центр",
"FBS для Ozon в Москве и МО: хранение товара на складе Преп-Центра, комплектация заказов, упаковка, печать этикеток, WMS и регулярные отгрузки в логистику Ozon.",
None, "фулфилмент FBS Ozon; хранение и сборка Ozon FBS", "commercial-marketplace-fbs"),
"/fbs-wildberries/": (
"Фулфилмент FBS Wildberries: хранение и сборка | Преп-Центр",
"FBS-фулфилмент для Wildberries: хранение на складе в Пушкино, сборка заказов, упаковка, маркировка, учет остатков через WMS и регулярные отгрузки на WB.",
None, "фулфилмент FBS Wildberries; сборка заказов ВБ FBS", "commercial-marketplace-fbs"),
"/fbs-yandex-market/": (
"Фулфилмент FBS Яндекс Маркета: сборка заказов | Преп-Центр",
"Фулфилмент FBS для Яндекс Маркета: приемка, хранение и сборка заказов, этикетки, возвраты, учет остатков через WMS и регулярная передача отправлений.",
None, "фулфилмент FBS Яндекс Маркет; сборка заказов FBS", "commercial-marketplace-fbs"),
"/fulfillment-bytovaya-himiya/": (
"Фулфилмент бытовой химии для Ozon и Wildberries | Преп-Центр",
"Фулфилмент бытовой химии в Москве и МО: приемка, проверка флаконов и канистр, защитная упаковка в ВПП и термоусадку, маркировка, FBO и FBS для Ozon и Wildberries.",
"Фулфилмент бытовой химии для Ozon, Wildberries и Яндекс Маркета",
"фулфилмент бытовой химии; упаковка бытовой химии для маркетплейсов", "commercial-category"),
"/fulfillment-shampuni-geli/": (
"Фулфилмент шампуней и гелей для Ozon и Wildberries | Преп-Центр",
"Подготовка шампуней и гелей для маркетплейсов в Москве и МО: контроль тары, упаковка в воздушно-пузырьковую и термоусадочную пленку, этикетки, FBO и FBS.",
"Фулфилмент шампуней и гелей для Ozon, Wildberries и Яндекс Маркета",
"фулфилмент шампуней и гелей; упаковка шампуней для WB и Ozon", "commercial-category"),
"/fulfillment-kosmetika/": (
"Фулфилмент косметики для Wildberries и Ozon в Москве | Преп-Центр",
"Фулфилмент косметики в Москве и МО: проверка, упаковка в ВПП, маркировка Честный знак, комплектация и поставки FBO/FBS на Wildberries и Ozon. Кейс 8 400 единиц.",
"Фулфилмент косметики для Wildberries и Ozon",
"фулфилмент косметики Москва; упаковка косметики Wildberries Ozon", "commercial-category"),
"/fulfillment-avtohimiya/": (
"Фулфилмент автохимии и автокосметики для маркетплейсов | Преп-Центр",
"Фулфилмент автохимии и автокосметики для Ozon и Wildberries: приемка, защитная упаковка, этикетки, маркировка, комплектация наборов, FBO и FBS. Склад в Пушкино.",
"Фулфилмент автохимии и автокосметики для маркетплейсов",
"фулфилмент автохимии; упаковка автокосметики Ozon WB", "commercial-category"),
"/fulfillment-stroitelnaya-himiya/": (
"Фулфилмент строительной химии для Ozon и Wildberries | Преп-Центр",
"Фулфилмент строительной химии: приемка, проверка герметиков и клеев, упаковка в термоусадку и ВПП, этикетки, FBO и FBS. Склад в Пушкино, реальные кейсы.",
"Фулфилмент строительной химии для Ozon и Wildberries",
"фулфилмент строительной химии; упаковка герметиков для маркетплейсов", "commercial-category"),
"/fulfillment-zhidkih-tovarov/": (
"Фулфилмент жидких товаров для Ozon и Wildberries | Преп-Центр",
"Фулфилмент жидких товаров в Москве и МО: проверка герметичности тары, защитная упаковка в ВПП и термоусадку, маркировка и поставки FBO/FBS на Wildberries и Ozon.",
None, "фулфилмент жидких товаров; упаковка жидкостей для маркетплейсов", "commercial-category"),
"/termousadka-vpp/": (
"Термоусадочная упаковка и ВПП для маркетплейсов | Преп-Центр",
"Упаковка товаров в термоусадочную и воздушно-пузырьковую пленку (ВПП, пупырку) для Wildberries и Ozon. Крупные партии, автоматическая линия, склад в Пушкино.",
None, "упаковка в термоусадочную пленку; упаковка в ВПП для маркетплейсов", "commercial-operation"),
"/chestnyy-znak/": (
"Маркировка Честный знак и КИЗ для Ozon, Wildberries | Преп-Центр",
"Печать и нанесение кодов DataMatrix, учет КИЗ через WMS МПФИТ и агрегация маркированных наборов. Маркировка товаров и упаковки для Wildberries, Ozon и Яндекс Маркета.",
None, "маркировка Честный знак для маркетплейсов; печать КИЗ DataMatrix", "commercial-operation"),
"/etiketki-marketpleysov/": (
"Этикетки для Wildberries и Ozon: печать и наклейка | Преп-Центр",
"Печать и наклейка штрихкодов и этикеток для Wildberries, Ozon и Яндекс Маркета. Маркировка товара, коробов и поставок FBO/FBS на складе в Пушкино.",
None, "наклейка этикеток Wildberries; печать этикеток Ozon; маркировка товара", "commercial-operation"),
"/komplektatsiya-naborov/": (
"Комплектация и сборка наборов для маркетплейсов | Преп-Центр",
"Комплектация наборов для Ozon и Wildberries: поштучная приемка, сборка по образцу, контроль комплектности, упаковка, маркировка. Реальный кейс 6 000 наборов за 5 дней.",
None, "комплектация наборов на заказ; сборка наборов для маркетплейсов", "commercial-operation"),
"/agregatsiya-kiz-naborov/": (
"Агрегация КИЗ наборов Честный знак через WMS | Преп-Центр",
"Сборка маркированных наборов и агрегация КИЗ: сканирование каждого вложения, связь кодов в WMS МПФИТ, печать внешней этикетки и передача файла соответствий.",
None, "агрегация КИЗ; маркировка наборов Честный знак", "commercial-operation"),
"/srochnaya-obrabotka-partiy/": (
"Срочная упаковка и маркировка партий для маркетплейсов | Преп-Центр",
"Срочная подготовка крупных партий для Wildberries и Ozon: приемка, упаковка в ВПП и термоусадку, этикетки, комплектация, FBO/FBS. До 20 000 единиц за смену на подходящих операциях.",
None, "срочная упаковка товаров; обработка партий маркетплейсы", "commercial-operation"),
"/upakovka-bytovoy-khimii/": (
"Упаковка бытовой химии: короба, материалы, маркировка | Преп-Центр",
"Упаковка бытовой химии: подбор картона, коробов и защитных вкладышей, требования к таре, печать и маркировка. Материалы, конструкции и этапы подготовки упаковки.",
"Упаковка бытовой химии: материалы и конструкции",
"упаковка бытовой химии коробки; материалы для упаковки бытовой химии", "informational-packaging-design"),
"/blog/": (
"Статьи о фулфилменте, FBO, FBS и упаковке товаров | Преп-Центр",
"Статьи Преп-Центра: требования Ozon, Wildberries и Яндекс Маркета, упаковка товаров, фулфилмент FBO/FBS, маркировка Честный знак, складской учет через WMS.",
"Статьи об упаковке товаров и фулфилменте",
"статьи фулфилмент; требования маркетплейсов; упаковка товаров", "informational-hub"),
"/cases/": (
"Кейсы фулфилмента: упаковка, маркировка, FBO/FBS | Преп-Центр",
"7 кейсов Преп-Центра: упаковка косметики, автохимии, ополаскивателей и строительной химии, сборка наборов, агрегация КИЗ и автоматизированная линия.",
"Кейсы фулфилмента и упаковки товаров для маркетплейсов",
"кейсы фулфилмента; упаковка товаров реальные примеры", "commercial-proof"),
"/online/": (
"Преп-Центр в интернете: профили, отзывы, публикации",
"Официальные профили Преп-Центра в Яндекс Картах, 2ГИС и каталогах фулфилмента, ссылки на отзывы, независимые рейтинги и публикации о компании.",
None, "Преп-Центр отзывы; Преп-Центр в интернете", "navigational"),
"/privacy-policy/": (
"Политика обработки персональных данных | Преп-Центр",
"Политика обработки персональных данных Преп-Центра: цели обработки, хранение, права посетителей, сведения о cookies и Яндекс.Метрике, контакты компании.",
None, "политика обработки персональных данных Преп-Центр", "legal"),
"/wms-mpfit-dlya-fulfillmenta/": (
"WMS МПФИТ: учет остатков и автоматизация фулфилмента | Преп-Центр",
"Как Преп-Центр использует WMS МПФИТ: единый остаток для Ozon и Wildberries, приемка, адресное хранение, учет КИЗ, FBO/FBS и личный кабинет клиента.",
"WMS МПФИТ в Преп-Центре: учет товаров и управление FBO/FBS",
"WMS МПФИТ для фулфилмента; учет остатков для WB и Ozon", "informational-wms"),
}

def sub_one(pattern, replacement, text, label, flags=re.I | re.S):
    out, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=flags)
    if count != 1:
        raise AssertionError(f"{label}: expected one replacement, got {count}")
    return out

def set_meta(text, name, value, attr="name"):
    pat = r'<meta\b[^>]*\b'+attr+r'=["\x27]'+re.escape(name)+r'["\x27][^>]*>'
    matches = list(re.finditer(pat, text, re.I))
    if len(matches) > 1:
        raise AssertionError(f"duplicate meta {name}")
    markup = '<meta '+attr+'="'+name+'" content="'+escape(value, quote=True)+'">'
    if not matches:
        if attr == "property":
            return sub_one(r"</head>", markup+"</head>", text, "insert "+name)
        raise AssertionError("Missing meta " + name)
    old = matches[0].group(0)
    # Replacing the full short meta tag prevents attribute-order edge cases.
    return text[:matches[0].start()] + markup + text[matches[0].end():]

def set_h1(text, new, route):
    # Restrict replacement to the single H1 within main, preserving its attributes.
    match = re.search(r"<main\b[^>]*>", text, re.I)
    end = text.find("</main>", match.end()) if match else -1
    if not match or end < 0:
        raise AssertionError("Missing <main> on " + route)
    body = text[match.end():end]
    items = list(re.finditer(r"(<h1\b[^>]*>)[\s\S]*?(</h1>)", body, re.I))
    if len(items) != 1:
        raise AssertionError("Expected exactly 1 main H1 on " + route)
    a = items[0]
    newh = a.group(1)+escape(new)+a.group(2)
    body = body[:a.start()] + newh + body[a.end():]
    return text[:match.end()] + body + text[end:]

def update_schema_core(text, new_title, new_description, new_h1):
    # Update the short site-entity block but leave long tariff and FAQ JSON-LD intact.
    pat = re.compile(r'(<!-- prep-center-schema-restore:start -->\s*<script type="application/ld\+json">)([\s\S]*?)(</script>)', re.I)
    def edit(m):
        doc = json.loads(m.group(2))
        dirty = False
        for node in doc.get("@graph", []):
            kind = node.get("@type", "")
            if kind == "WebPage":
                if node.get("name") != new_title:
                    node["name"] = new_title
                    dirty = True
                if "description" in node and node["description"] != new_description:
                    node["description"] = new_description
                    dirty = True
        if not dirty:
            return m.group(0)
        return m.group(1) + json.dumps(doc, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + m.group(3)
    out, n = pat.subn(edit, text, count=1)
    if n != 1:
        raise AssertionError("Canonical schema block missing")
    return out

def optimize_page(source, route):
    if route not in SEO:
        return source
    title, description, h1, cluster, intent = SEO[route]
    current_title = BeautifulSoup(source, "html.parser").title.get_text(" ", strip=True)
    current_description = BeautifulSoup(source.split("</head>")[0]+"</head>", "html.parser").find("meta", attrs={"name": "description"}).get("content", "")
    if current_title == title and current_description == description and h1 is None:
        # May still need OG sync; safe to run all transformations anyway.
        pass
    result = sub_one(r"<title\b[^>]*>[\s\S]*?</title>", "<title>"+escape(title)+"</title>", source, "title "+route)
    result = set_meta(result, "description", description)
    result = set_meta(result, "og:title", title, "property")
    result = set_meta(result, "og:description", description, "property")
    if h1 is not None:
        result = set_h1(result, h1, route)
    if route == "/":
        # Heading remains visually prominent; make the service cluster explicit.
        result = sub_one(r"<h2>\s*Наши услуги\s*</h2>", "<h2>Услуги фулфилмента для маркетплейсов</h2>", result, "home H2")
    result = update_schema_core(result, title, description, h1)
    return result

def git_changed_date(rel):
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cs", "--", rel],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", out):
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    return None

def sitemap_with_correct_dates(source, routes, edited):
    ns="http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", ns)
    root=ET.fromstring(source)
    locs=[]
    changed_dates={}
    today=datetime.now(timezone.utc).date().isoformat()
    for entry in root.findall("{%s}url"%ns):
        urltag=entry.find("{%s}loc"%ns)
        assert urltag is not None and urltag.text
        url=urltag.text.strip()
        route=url.replace(BASE,"",1)
        if route not in routes:
            raise AssertionError("Unexpected sitemap route: "+route)
        locs.append(url)
        path="index.html" if route=="/" else route.strip("/")+"/index.html"
        value=today if route in edited else git_changed_date(path)
        if not value:
            raise AssertionError("No verified git lastmod date for "+path)
        mod=entry.find("{%s}lastmod"%ns)
        if mod is None:
            mod=ET.SubElement(entry,"{%s}lastmod"%ns)
        mod.text=value
        changed_dates[route]=value
    if len(locs)!=45 or set(locs)!={BASE+r for r in routes}:
        raise AssertionError("Sitemap must contain exactly all 45 canonical URLs")
    ET.indent(root, space="  ")
    raw=ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")+"\n"
    return raw, changed_dates

def main():
    check="--check" in sys.argv
    inv=json.loads((ROOT/"restoration/page-inventory.json").read_text(encoding="utf-8"))
    routes=sorted({x["path"] for x in inv if x.get("group") in GROUPS})
    assert len(routes)==45
    assert set(SEO).issubset(routes)
    edits, changed=[],[]
    for route in routes:
        path=ROOT/("index.html" if route=="/" else route.strip("/")+"/index.html")
        original=path.read_text(encoding="utf-8")
        new=optimize_page(original,route)
        if new != original:
            edits.append(route)
            if not check:
                path.write_text(new,encoding="utf-8")
        t,d,header = None,None,None
        html=BeautifulSoup(new,"html.parser")
        meta=html.head.find("meta",attrs={"name":"description"})
        title=html.title.get_text(" ",strip=True)
        description=meta.get("content","") if meta else ""
        heading=html.main.find("h1")
        h1=heading.get_text(" ",strip=True) if heading else ""
        if not title or not description or not h1:
            raise AssertionError("Missing SEO content for "+route)
        if route in SEO:
            expectedTitle, expectedDescription, expectedH1,cluster,intent=SEO[route]
            if title!=expectedTitle or description!=expectedDescription:
                raise AssertionError("Metadata differs from target on "+route)
            if expectedH1 and h1!=expectedH1:
                raise AssertionError("H1 differs from intent on "+route)
            if html.head.find("meta",attrs={"property":"og:title"}).get("content") != expectedTitle:
                raise AssertionError("OG title doesn't match "+route)
        changed.append({"route":route,"intent":SEO[route][4] if route in SEO else "preserved",
                        "primary_query_cluster":SEO[route][3] if route in SEO else None,
                        "title":title,"description":description,"h1":h1,
                        "modified":route in edits})
    map_path=ROOT/"sitemap.xml"
    xml_old=map_path.read_text(encoding="utf-8")
    xml_new,lastmods=sitemap_with_correct_dates(xml_old,routes,set(SEO))
    # Running --check after commit should not depend on uncommitted file statuses.
    # SEO routes all changed, and untouched routes use real Git history dates.
    if not check and xml_new!=xml_old:
        map_path.write_text(xml_new,encoding="utf-8")
    if check:
        if edits:
            raise AssertionError("Unapplied SEO edits: "+str(edits))
        if xml_new!=xml_old:
            raise AssertionError("Sitemap dates not current: run optimizer")
    else:
        output={
            "basis":"Current site content and intent hypotheses; no Wordstat volume measurements",
            "optimized_at_utc":datetime.now(timezone.utc).isoformat(),
            "checked_pages":len(routes),
            "edited_pages":edits,
            "keyword_map":changed,
            "sitemap_lastmod":lastmods
        }
        p=ROOT/"reports/seo-keyword-map-20261112.json"
        p.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"mode":"check" if check else "write",
                      "pages":len(routes),"targeted_routes":len(SEO),
                      "rewritten_pages":len(edits),"sitemap":len(lastmods)},
                     ensure_ascii=False))

if __name__=="__main__":
    main()
