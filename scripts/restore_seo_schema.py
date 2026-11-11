#!/usr/bin/env python3
"""Restore canonical schema.org, person/entity links and metadata on 45 static pages.

Sources: 2026-08-22 HTML archive (restoration/source), autumn page inventory,
the latest visible content of each page, and the current /online/ profile list.
This script does NOT restore stale AggregateRating, bot protection, tracking
scripts or defunct Bitrix/PHP endpoints. Run repeatedly without duplications.
"""
from __future__ import annotations

from bs4 import BeautifulSoup
from html import escape
from pathlib import Path
from urllib.parse import urljoin
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://prep-center.ru"
ORG_ID = BASE + "/#organization"
SITE_ID = BASE + "/#website"
BRAND_ID = BASE + "/#brand"
LOGO_ID = BASE + "/#logo"
PERSON_ID = BASE + "/about/#alexander-alkhov"
CATALOG_ID = BASE + "/#offer-catalog"
DETAILED_CATALOG_ID = BASE + "/tarify/#catalog"
START = "<!-- prep-center-schema-restore:start -->"
END = "<!-- prep-center-schema-restore:end -->"
PIXEL = "<!-- prep-center-metrika-noscript -->"
GROUPS = {
    "Услуги и категории", "Статьи и требования маркетплейсов",
    "Кейсы", "Основные страницы",
}

# These profiles are also present in the current, publicly visible /online/
# directory. Retain the exact stable external URLs of the old entity, except
# where the new directory has a more suitable current link.
SAME_AS = [
    "https://преп-центр.рф/",
    "https://prep-center.clients.site/",
    "https://yandex.ru/maps/org/prep_tsentr/113144699853/",
    "https://2gis.ru/pushkino/firm/70000001056306402",
    "https://uslugi.yandex.ru/profile/Prepcentr-3389756",
    "https://zoon.ru/msk/business/fulfilment_dlya_marketplejsov_prep-tsentr/",
    "https://full-full.ru/fulfilmenty/prep-czentr/",
    "https://sellermap.online/services_for_marketplaces/prep-tsentr.784/",
    "https://fulex.pro/list/suppliers/d5c6ae70-06b6-45eb-b9fa-9f3d4431713a",
    "https://4sellers.ru/blog/listing/prep-centr/",
    "https://msk.yp.ru/detail/id/prep_tsentr_5200927/",
    "https://www.yell.ru/moscow/com/prep-centr_14521918/",
    "https://moscow.flamp.ru/firm/prep_centr_kompaniya_po_uslugam_fulfilmenta-70000001056306402",
    "https://prep-center.pulscen.ru/",
    "https://vk.com/prepcentermp",
    "https://instagram.com/prepcentermp",
    "https://t.me/prepmanager2",
]
WEB_SITE = {
    "@type": "WebSite", "@id": SITE_ID, "url": BASE + "/",
    "name": "Преп-Центр", "alternateName": ["Prep Center", "Prep-Center", "Преп Центр"],
    "inLanguage": "ru-RU", "publisher": {"@id": ORG_ID},
}
ORG = {
    "@type": ["Organization", "LocalBusiness"], "@id": ORG_ID,
    "name": "Преп-Центр", "legalName": "ООО «ПРЕП-ЦЕНТР»",
    "foundingDate": "2017-03-31",  # legal entity, not start of fulfillment operations
    "alternateName": ["Преп Центр", "Prep Center", "Prep-Center", "PrepCenter"],
    "url": BASE + "/",
    "description": "Фулфилмент, приемка, сортировка, упаковка, маркировка и подготовка поставок для Wildberries, Ozon и Яндекс Маркета. Склад в Пушкино.",
    "logo": {"@id": LOGO_ID},
    "image": BASE + "/assets/about-01-sklad-rabochie-zony.webp",
    "brand": {"@id": BRAND_ID},
    "telephone": "+7-930-600-75-20",
    "email": "info@prep-center.ru",
    "address": {
        "@type": "PostalAddress", "postalCode": "141201",
        "streetAddress": "ул. Новая, д. 10", "addressLocality": "Пушкино",
        "addressRegion": "Московская область", "addressCountry": "RU",
    },
    "geo": {"@type": "GeoCoordinates", "latitude": 56.0017485, "longitude": 37.7976532},
    "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "08:00", "closes": "20:00",
    }],
    "contactPoint": [
        {"@type": "ContactPoint", "contactType": "sales",
         "telephone": "+7-930-600-75-20", "email": "info@prep-center.ru",
         "availableLanguage": "ru", "areaServed": "RU"},
        {"@type": "ContactPoint", "contactType": "customer service",
         "url": "https://t.me/prepmanager2",
         "availableLanguage": "ru", "areaServed": "RU"},
    ],
    "hasMap": "https://yandex.ru/maps/org/prep_tsentr/113144699853/",
    "areaServed": [{"@type": "Country", "name": "Россия"},
                   {"@type": "City", "name": "Москва"},
                   {"@type": "AdministrativeArea", "name": "Московская область"}],
    "currenciesAccepted": "RUB",
    "sameAs": SAME_AS,
    "hasOfferCatalog": {"@id": CATALOG_ID},
    "knowsAbout": [
        "Фулфилмент для Wildberries и Ozon", "FBO", "FBS",
        "Упаковка бытовой химии", "Упаковка шампуней и гелей",
        "Упаковка косметики", "Автохимия", "Строительная химия",
        "Воздушно-пузырьковая пленка", "Термоусадочная упаковка",
        "Маркировка Честный знак", "Комплектация товарных наборов",
    ],
    "additionalProperty": [
        {"@type": "PropertyValue", "name": "Начало работы в фулфилменте", "value": "2019"},
        {"@type": "PropertyValue", "name": "Площадь склада", "value": "1560 м²"},
        {"@type": "PropertyValue", "name": "Производительность", "value": "до 20 000 единиц за 12-часовую смену"},
        {"@type": "PropertyValue", "name": "Складская WMS", "value": "МПФИТ"},
    ],
    "identifier": [
        {"@type": "PropertyValue", "propertyID": "ИНН", "value": "5038126700"},
        {"@type": "PropertyValue", "propertyID": "ОГРН", "value": "1175050003039"},
    ],
}
BRAND = {"@type": "Brand", "@id": BRAND_ID, "name": "Преп-Центр",
         "alternateName": ["Prep Center", "Prep-Center", "Преп Центр"],
         "url": BASE + "/", "logo": {"@id": LOGO_ID}}
LOGO = {"@type": "ImageObject", "@id": LOGO_ID,
        "url": BASE + "/assets/prep-center-logo.svg",
        "contentUrl": BASE + "/assets/prep-center-logo.svg",
        "caption": "Логотип Преп-Центра"}
PERSON = {"@type": "Person", "@id": PERSON_ID,
          "name": "Александр Анатольевич Альхов",
          "jobTitle": "Директор", "worksFor": {"@id": ORG_ID},
          "url": BASE + "/about/"}
SERVICE_CATALOG = [
    ("Фулфилмент для бытовой химии", "/fulfillment-bytovaya-himiya/"),
    ("Фулфилмент для шампуней и гелей", "/fulfillment-shampuni-geli/"),
    ("Фулфилмент для косметики", "/fulfillment-kosmetika/"),
    ("Фулфилмент для автохимии", "/fulfillment-avtohimiya/"),
    ("Фулфилмент для строительной химии", "/fulfillment-stroitelnaya-himiya/"),
    ("Фулфилмент жидких товаров", "/fulfillment-zhidkih-tovarov/"),
    ("Термоусадка и упаковка в ВПП", "/termousadka-vpp/"),
    ("Наклейка этикеток маркетплейсов", "/etiketki-marketpleysov/"),
    ("Маркировка Честный знак", "/chestnyy-znak/"),
    ("Комплектация товарных наборов", "/komplektatsiya-naborov/"),
    ("Подготовка поставок FBO", "/fulfillment-fbo/"),
    ("Обработка заказов FBS", "/fulfillment-fbs/"),
]
MANIFEST = {
    "name": "Преп-Центр", "short_name": "Преп-Центр", "lang": "ru",
    "start_url": "/", "scope": "/", "display": "browser",
    "background_color": "#ffffff", "icons": [
        {"src": "/favicon-96x96.png", "sizes": "96x96", "type": "image/png"},
        {"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
    ]
}


def plain(tag) -> str:
    return re.sub(r"\s+", " ", tag.get_text(" ", strip=True)).strip() if tag else ""


def abs_url(value: str) -> str:
    if not value or value.startswith(("data:", "javascript:")):
        return BASE + "/assets/hero.webp"
    return urljoin(BASE + "/", value)


def faq_nodes(soup):
    items = []
    for detail in soup.select("main #questions details.faq-item"):
        summary = detail.find("summary", recursive=False)
        if not summary:
            continue
        question = re.sub(r"\s*\+\s*$", "", plain(summary)).strip()
        answers = [plain(child) for child in detail.children
                   if getattr(child, "name", None) and child.name != "summary"]
        answer = re.sub(r"\s+", " ", " ".join(x for x in answers if x)).strip()
        if question and answer:
            items.append({"@type": "Question", "name": question,
                          "acceptedAnswer": {"@type": "Answer", "text": answer}})
    return items


def case_nodes(soup):
    items, seen = [], set()
    for card in soup.select("main .home-case-grid .home-case-card"):
        link = card.select_one('a[href^="/cases/"]')
        if not link:
            continue
        href = link.get("href", "").split("?")[0]
        if href in seen:
            continue
        seen.add(href)
        title = plain(card.find(["h2", "h3"])) or plain(link)
        if title:
            items.append({"@type": "ListItem", "position": len(items) + 1,
                          "name": title, "url": abs_url(href)})
    return items


def meta_is_present(soup, attr, name):
    return bool(soup.head.find("meta", attrs={attr: name})) if soup.head else False


def build_insert(soup, route, canonical, title, description):
    graph = [WEB_SITE, ORG, BRAND, LOGO]
    if route == "/about/":
        graph.append(PERSON)
    if route == "/":
        faq = faq_nodes(soup)
        cases = case_nodes(soup)
        if len(faq) < 5 or len(cases) < 5:
            raise AssertionError("Home FAQ/case cards not reliably parsed: %d FAQ, %d cases" % (len(faq), len(cases)))
        graph.append({
            "@type": "WebPage", "@id": canonical + "#webpage",
            "url": canonical, "name": title, "description": description,
            "isPartOf": {"@id": SITE_ID}, "about": {"@id": ORG_ID},
            "mainEntity": {"@id": canonical + "#fulfillment-service"},
            "hasPart": [{"@id": canonical + "#faq"}, {"@id": canonical + "#case-list"}],
            "inLanguage": "ru-RU",
        })
        graph.append({
            "@type": "Service", "@id": canonical + "#fulfillment-service",
            "name": "Фулфилмент и подготовка товаров к маркетплейсам",
            "serviceType": "Фулфилмент для Wildberries, Ozon и Яндекс Маркета",
            "provider": {"@id": ORG_ID},
            "areaServed": ["Москва", "Московская область"],
            "hasOfferCatalog": {"@id": CATALOG_ID},
            "url": canonical,
        })
        graph.append({
            "@type": "OfferCatalog", "@id": CATALOG_ID,
            "name": "Услуги Преп-Центра", "url": BASE + "/tarify/",
            "numberOfItems": len(SERVICE_CATALOG),
            "itemListElement": [
                {"@type": "Offer", "url": BASE + route_path,
                 "seller": {"@id": ORG_ID},
                 "itemOffered": {"@type": "Service",
                                 "@id": BASE + route_path + "#service",
                                 "name": label, "url": BASE + route_path,
                                 "provider": {"@id": ORG_ID}}}
                for label, route_path in SERVICE_CATALOG
            ],
        })
        graph.append({"@type": "ItemList", "@id": canonical + "#case-list",
                      "name": "Примеры поставок Преп-Центра",
                      "numberOfItems": len(cases), "itemListElement": cases})
        graph.append({"@type": "FAQPage", "@id": canonical + "#faq",
                      "name": "Вопросы и ответы о Преп-Центре",
                      "isPartOf": {"@id": canonical + "#webpage"},
                      "mainEntity": faq})
    elif route == "/about/":
        graph.append({
            "@type": "WebPage", "@id": canonical + "#webpage",
            "url": canonical, "name": title,
            "isPartOf": {"@id": SITE_ID}, "about": {"@id": ORG_ID},
            "mainEntity": {"@id": ORG_ID}, "mentions": {"@id": PERSON_ID},
            "inLanguage": "ru-RU",
        })

    ld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                    ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    out = [START, '<script type="application/ld+json">' + ld + "</script>"]

    if not meta_is_present(soup, "property", "og:title"):
        out.append('<meta property="og:title" content="' + escape(title, quote=True) + '">')
    if not meta_is_present(soup, "property", "og:description"):
        out.append('<meta property="og:description" content="' + escape(description, quote=True) + '">')
    if not meta_is_present(soup, "property", "og:url"):
        out.append('<meta property="og:url" content="' + escape(canonical, quote=True) + '">')
    existing_types = []
    for sc in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            obj = json.loads(sc.string or sc.get_text())
            existing_types.append(obj.get("@type") if isinstance(obj, dict) else None)
        except (ValueError, TypeError):
            pass
    article = route.startswith("/cases/") and route != "/cases/" or "Article" in existing_types
    if not meta_is_present(soup, "property", "og:type"):
        out.append('<meta property="og:type" content="' + ("article" if article else "website") + '">')
    if not meta_is_present(soup, "property", "og:image"):
        main = soup.find("main")
        imgs = (main.select('img[src]') if main else [])
        src = ("/assets/hero.webp" if route == "/" else next(
            (i["src"] for i in imgs
             if not i["src"].lower().split("?")[0].endswith(".svg")
             and "logo" not in i["src"].lower()), "/assets/hero.webp"))
        out.append('<meta property="og:image" content="' + escape(abs_url(src), quote=True) + '">')
    if not meta_is_present(soup, "name", "twitter:card"):
        out.append('<meta name="twitter:card" content="summary_large_image">')
    if not meta_is_present(soup, "name", "apple-mobile-web-app-title"):
        out.append('<meta name="apple-mobile-web-app-title" content="Преп-Центр">')
    if not soup.head.find("link", rel="manifest"):
        out.append('<link rel="manifest" href="/site.webmanifest">')
    out.append(END)
    return "\n".join(out) + "\n"


def enrich_existing_ld(source, route):
    # Preserve the full original tariff catalog, service/pricing, FAQ and article
    # payloads, changing only missing identity references in the top-level node.
    pattern = re.compile(r'(<script\b[^>]*type=["\x27]application/ld\+json["\x27][^>]*>)([\s\S]*?)(</script>)', re.I)
    def change(match):
        try:
            val = json.loads(match.group(2))
        except json.JSONDecodeError:
            raise AssertionError("Invalid original JSON-LD: " + route)
        if not isinstance(val, dict):
            return match.group(0)
        kind = val.get("@type")
        kinds = kind if isinstance(kind, list) else [kind]
        modified = False
        if "Service" in kinds:
            if not val.get("provider"):
                val["provider"] = {"@id": ORG_ID}
                modified = True
            if not val.get("@id"):
                val["@id"] = BASE + route + "#service"
                modified = True
        if "Article" in kinds or "BlogPosting" in kinds:
            author = val.get("author")
            if isinstance(author, dict) and author.get("@type") == "Organization" and author.get("name", "").lower().startswith("преп"):
                if author.get("@id") != ORG_ID:
                    author["@id"] = ORG_ID
                    modified = True
        if kind in ("AboutPage", "ContactPage", "CollectionPage", "WebPage"):
            if "isPartOf" not in val:
                val["isPartOf"] = {"@id": SITE_ID}
                modified = True
            if "about" not in val:
                val["about"] = {"@id": ORG_ID}
                modified = True
        if not modified:
            return match.group(0)
        return match.group(1) + json.dumps(val, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + match.group(3)
    return pattern.sub(change, source)


def restore_page(original, route):
    cleaned = re.sub(re.escape(START) + r"[\s\S]*?" + re.escape(END) + r"\s*", "", original)
    cleaned = enrich_existing_ld(cleaned, route)
    soup = BeautifulSoup(cleaned, "html.parser")
    if soup.head is None or soup.body is None:
        raise AssertionError("Missing head/body on " + route)
    title = plain(soup.head.find("title"))
    canonical_tag = soup.head.find("link", rel="canonical")
    canonical = canonical_tag.get("href", "") if canonical_tag else ""
    expected = BASE + route
    if not title or canonical != expected:
        raise AssertionError("Bad title or canonical on %s: %s" % (route, canonical))
    meta = soup.head.find("meta", attrs={"name": "description"})
    description = meta.get("content", "").strip() if meta else ""
    if not description:
        raise AssertionError("No description on " + route)
    addition = build_insert(soup, route, canonical, title, description)
    result, n = re.subn(r"</head\s*>", lambda m: addition + m.group(0), cleaned, count=1, flags=re.I)
    if n != 1:
        raise AssertionError("Can't insert head on " + route)
    if "mc.yandex.ru/watch/100290924" not in result:
        pix = PIXEL + '<noscript><div><img src="https://mc.yandex.ru/watch/100290924" style="position:absolute;left:-9999px" alt=""></div></noscript>\n'
        result, n = re.subn(r"<body\b[^>]*>", lambda m: m.group(0) + "\n" + pix, result, count=1, flags=re.I)
        if n != 1:
            raise AssertionError("Can't insert no-JS pixel on " + route)
    parsed = BeautifulSoup(result, "html.parser")
    scripts = parsed.find_all("script", attrs={"type": "application/ld+json"})
    for script in scripts:
        json.loads(script.string or script.get_text())
    schemas = [json.loads(script.string or script.get_text()) for script in scripts]
    orgs = [n for obj in schemas if isinstance(obj, dict) for n in obj.get("@graph", [])
            if n.get("@id") == ORG_ID]
    if len(orgs) != 1 or len([m for m in parsed.head.find_all("meta", attrs={"property": "og:title"})]) != 1:
        raise AssertionError("Duplicate/missing entity or social metadata on " + route)
    if not parsed.head.find("link", rel="manifest") or not parsed.head.find("meta", attrs={"name": "apple-mobile-web-app-title"}):
        raise AssertionError("Missing manifest or mobile metadata " + route)
    if not parsed.body.find("img", src="https://mc.yandex.ru/watch/100290924"):
        raise AssertionError("Missing no-script analytics fallback on " + route)
    if result.count(START) != 1 or result.count(END) != 1:
        raise AssertionError("Duplicate schema block on " + route)
    return result, len(scripts)


def main():
    check = "--check" in sys.argv
    inventory = json.loads((ROOT / "restoration/page-inventory.json").read_text(encoding="utf-8"))
    routes = sorted({e["path"] for e in inventory if e.get("group") in GROUPS})
    assert len(routes) == 45, "Expected 45 pages; got %d" % len(routes)
    online = (ROOT / "online/index.html").read_text(encoding="utf-8")
    if sum(u in online for u in SAME_AS) < 12:
        raise AssertionError("Current /online/ does not confirm the majority of sameAs profiles")
    changed, checked = [], []
    for route in routes:
        p = ROOT / route.strip("/") / "index.html"
        if route == "/":
            p = ROOT / "index.html"
        before = p.read_text(encoding="utf-8")
        after, nodes = restore_page(before, route)
        checked.append({"path": route, "json_ld_blocks": nodes,
                        "new_schema": True, "open_graph": True,
                        "manifest": True, "metrika_noscript": True})
        if after != before:
            changed.append(route)
            if not check:
                p.write_text(after, encoding="utf-8")
    expected_manifest = json.dumps(MANIFEST, ensure_ascii=False, indent=2) + "\n"
    manifest_path = ROOT / "site.webmanifest"
    if check:
        if changed:
            raise AssertionError("Schema not idempotent / uncommitted pages: " + str(changed))
        if not manifest_path.is_file() or manifest_path.read_text(encoding="utf-8") != expected_manifest:
            raise AssertionError("Missing/changed manifest")
    else:
        manifest_path.write_text(expected_manifest, encoding="utf-8")
        report = {
            "scope": "45 canonical pages", "source": [
                "22.08.2026 saved HTML", "20-21.10.2026 editorial/source materials",
                "04.11.2026 index inventory", "current published text and /online/ directory",
            ], "total_pages": len(checked), "changed_routes": changed,
            "sameAs_count": len(SAME_AS),
            "notes": [
                "No unverified October full HTML was assumed.",
                "Stale historical AggregateRating/review counts were not copied.",
                "Old Botfaqtor, UIS, Bitrix scripts were not restored.",
                "Existing 134 tariff entries and individual Service/Article/FAQ markup preserved.",
                "Original counter 100290924 is unchanged; noscript fallback added.",
            ], "pages": checked,
        }
        (ROOT / "reports/schema-restore-20261111.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mode": "check" if check else "write",
                      "pages": len(checked), "changed": len(changed),
                      "sameAs": len(SAME_AS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
