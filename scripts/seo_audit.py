#!/usr/bin/env python3
"""Audit every canonical Prep-Center URL, its head metadata and H1-H3.

Source of truth: current repository files + restoration/page-inventory.json.
No claimed query frequency is inferred from page text. This is a technical and
semantic on-page audit, not data from Wordstat or Search Console.
"""
from __future__ import annotations

import collections
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://prep-center.ru"
GROUPS = {"Услуги и категории", "Статьи и требования маркетплейсов", "Кейсы", "Основные страницы"}
REPORT_PHASE = "after" if "--after" in sys.argv else "before"
OUT_JSON = ROOT / ("reports/seo-audit-" + REPORT_PHASE + "-20261112.json")
OUT_MD = ROOT / ("reports/seo-audit-" + REPORT_PHASE + "-20261112.md")


def clean(text):
    return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ")).strip()


def gather(route):
    path = ROOT / route.strip("/") / "index.html" if route != "/" else ROOT / "index.html"
    raw = path.read_text(encoding="utf-8")
    html = BeautifulSoup(raw, "html.parser")
    head, main = html.head, html.main
    titles = [clean(x.get_text(" ", strip=True)) for x in head.find_all("title")]
    descriptions = [clean(x.get("content")) for x in head.find_all("meta", attrs={"name": re.compile(r"^description$", re.I)})]
    canonical = [x.get("href", "") for x in head.find_all("link", rel="canonical")]
    robots = [x.get("content", "") for x in head.find_all("meta", attrs={"name": re.compile(r"^robots$", re.I)})]
    headings = {str(n): [clean(x.get_text(" ", strip=True)) for x in main.find_all("h" + str(n))] for n in (1, 2, 3)}
    heading_stack = [(int(x.name[1]), clean(x.get_text(" ", strip=True))) for x in main.find_all(re.compile(r"^h[1-3]$"))]
    skips = []
    for (prev,_), (curr, label) in zip(heading_stack, heading_stack[1:]):
        if curr > prev + 1:
            skips.append({"from": prev, "to": curr, "heading": label[:75]})
    issues = []
    if len(titles) != 1 or not titles[0]:
        issues.append("title: missing/duplicate")
    if len(descriptions) != 1 or not descriptions[0]:
        issues.append("description: missing/duplicate")
    if len(canonical) != 1 or canonical[0] != BASE + route:
        issues.append("canonical: missing/incorrect/duplicate")
    if len(robots) != 1 or "index" not in robots[0].lower() or "noindex" in robots[0].lower():
        issues.append("robots: missing/blocked/duplicate")
    if len(headings["1"]) != 1:
        issues.append("H1: missing/duplicate")
    if any(not x for x in (headings["1"] + headings["2"] + headings["3"])):
        issues.append("H1-H3: empty heading")
    if skips:
        issues.append("heading hierarchy skip")
    if len(titles) == 1 and len(titles[0]) > 90:
        issues.append("title: overly long")
    if len(titles) == 1 and len(titles[0]) < 30:
        issues.append("title: weak/short (review)")
    if len(descriptions) == 1 and len(descriptions[0]) < 85:
        issues.append("description: weak/short (review)")
    if len(descriptions) == 1 and len(descriptions[0]) > 220:
        issues.append("description: lengthy (review)")
    if raw.lower().count('rel="canonical"') != 1:
        issues.append("canonical raw count != 1")
    return {
        "url": BASE + route,
        "route": route,
        "file": path.relative_to(ROOT).as_posix(),
        "title": titles[0] if titles else None,
        "title_count": len(titles),
        "title_len": len(titles[0]) if titles else 0,
        "description": descriptions[0] if descriptions else None,
        "description_count": len(descriptions),
        "description_len": len(descriptions[0]) if descriptions else 0,
        "canonical": canonical,
        "robots": robots,
        "h1": headings["1"],
        "h2": headings["2"],
        "h3": headings["3"],
        "heading_skips": skips,
        "issues": issues
    }


def main():
    inv = json.loads((ROOT / "restoration/page-inventory.json").read_text(encoding="utf-8"))
    routes = sorted({e["path"] for e in inv if e.get("group") in GROUPS})
    assert len(routes) == 45, "Expected exactly 45 canonical content pages"
    pages = [gather(route) for route in routes]
    counts = collections.Counter(issue for p in pages for issue in p["issues"])
    for field in ("title", "description"):
        groups = collections.defaultdict(list)
        for p in pages:
            if p[field]:
                groups[p[field].casefold()].append(p["route"])
        for value, group in groups.items():
            if len(group) > 1:
                counts["duplicate " + field] += len(group)
                for route in group:
                    next(p for p in pages if p["route"] == route)["issues"].append("duplicate " + field)
    sitemap_xml = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    root = ET.fromstring(sitemap_xml)
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    sm_urls = [clean(x.text) for x in root.findall(".//" + ns + "loc")]
    sm_mods = [clean(x.text) for x in root.findall(".//" + ns + "lastmod")]
    expected_urls = [BASE + r for r in routes]
    sitemap = {
        "url_count": len(sm_urls),
        "unique": len(set(sm_urls)) == len(sm_urls),
        "missing": sorted(set(expected_urls) - set(sm_urls)),
        "extra": sorted(set(sm_urls) - set(expected_urls)),
        "lastmod_values": dict(collections.Counter(sm_mods))
    }
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "GitHub repository main, original HTML (not browser-rendered DOM)",
        "total_pages": len(pages),
        "issue_counts": dict(counts.most_common()),
        "sitemap": sitemap,
        "robots_txt": robots,
        "pages": pages
    }
    if "--check" in sys.argv:
        assert sitemap["url_count"] == 45 and not sitemap["missing"] and not sitemap["extra"]
        assert not any(p["title_count"] != 1 or p["description_count"] != 1 or p["h1"] == [] or len(p["h1"]) > 1 or p["canonical"] != [p["url"]] for p in pages)
        assert len({p["title"].casefold() for p in pages}) == 45, "Duplicate titles"
        assert len({p["description"].casefold() for p in pages}) == 45, "Duplicate descriptions"
        assert all(p["robots"] == ["index,follow"] for p in pages), "Blocked robots"
        assert not any(p["heading_skips"] for p in pages), "Heading hierarchy gaps"
        print(json.dumps({"pages": 45, "basic_seo": "valid", "issue_counts": dict(counts)}, ensure_ascii=False))
        return
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Аудит SEO: все 45 страниц prep-center.ru", "",
        "Срез исходников ветки main. Частотность запросов Wordstat не замерялась.", "",
        f"Проверено страниц: **{len(pages)}**. В sitemap: **{len(sm_urls)}** URL.", "",
        "## Замечания", "",
    ]
    lines.extend("- " + k + ": **" + str(v) + "**" for k,v in counts.most_common())
    lines += ["", "## Sitemap", "",
              "- Missing: " + str(len(sitemap["missing"])),
              "- Extra: " + str(len(sitemap["extra"])),
              "- lastmod: " + ", ".join(k + " — " + str(v) for k,v in sitemap["lastmod_values"].items()), "",
              "## Title, Description, заголовки и замечания по всем URL", ""]
    for p in pages:
        lines += [
            "### " + p["route"],
            "- **Title** (" + str(p["title_len"]) + "): " + (p["title"] or "ОТСУТСТВУЕТ"),
            "- **Description** (" + str(p["description_len"]) + "): " + (p["description"] or "ОТСУТСТВУЕТ"),
            "- **H1**: " + " | ".join(p["h1"]),
            "- **H2**: " + " | ".join(p["h2"][:12]) + (" …" if len(p["h2"]) > 12 else ""),
            "- **H3**: " + " | ".join(p["h3"][:10]) + (" …" if len(p["h3"]) > 10 else ""),
            "- **Замечания**: " + (", ".join(p["issues"]) or "технически корректно"),
            ""
        ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"pages": len(pages), "issues": dict(counts.most_common()), "sitemap": sitemap}, ensure_ascii=False))


if __name__ == "__main__":
    main()
