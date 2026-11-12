#!/usr/bin/env python3
"""Restore a real cookie choice across 45 pages without disturbing their markup.

The canonical shared JS inserts the notice and controls Yandex.Metrika.
This update removes the no-JS tracking pixel, which bypassed opt-in,
never migrates implicit legacy cookieAccepted into explicit consent,
and is validated in Chromium using the runner's installed Chrome channel.
bumps the shared JS asset version, extends the policy, and corrects the
schema generator so it will never reintroduce a pre-consent pixel.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS_VERSION = "20261111-cookie-v1"
GROUPS = {
    "Услуги и категории", "Статьи и требования маркетплейсов",
    "Кейсы", "Основные страницы",
}
PIXEL_RE = re.compile(
    r"<!-- prep-center-metrika-noscript -->\s*<noscript>"
    r"[\s\S]*?mc\.yandex\.ru/watch/100290924[\s\S]*?</noscript>\s*",
    re.I,
)
SHARED_JS_RE = re.compile(
    r'(<script\b[^>]*\bsrc="/assets/shared-components\.js)'
    r'(?:\?[^"]*)?("[^>]*></script>)',
    re.I,
)
POLICY_START = "<!-- prep-cookie-policy:start -->"
POLICY_END = "<!-- prep-cookie-policy:end -->"
POLICY_ANCHOR = (
    '<p>Актуальная версия политики опубликована по адресу '
    '<a href="/privacy-policy/">https://prep-center.ru/privacy-policy</a>.</p>'
)
POLICY_CONTENT = """<!-- prep-cookie-policy:start -->
<h2 id="cookies-and-analytics">13. Файлы cookie и веб-аналитика</h2>
<p>Для работы сайта могут использоваться технические файлы cookie и локальное хранилище браузера. В локальном хранилище записывается выбор посетителя о подключении необязательной аналитики. Этот выбор сохраняется на срок до 180 дней и может быть изменен в любое время.</p>
<p>Если посетитель разрешает аналитику, сайт подключает Яндекс.Метрику (счетчик № 100290924), включая Вебвизор и карту кликов. Сервис помогает анализировать посещаемость, источники переходов и взаимодействия с элементами сайта. Яндекс.Метрика может использовать файлы cookie и локальное хранилище для идентификации браузера. <a href="https://yandex.ru/support/metrica/ru/general/cookie-usage.html" target="_blank" rel="noopener">Подробнее о данных Яндекс.Метрики</a>.</p>
<p>До разрешения аналитики и при выборе «Только необходимые» счетчик Яндекс.Метрики не подключается. Изменить решение можно с помощью кнопки «Настройки cookies» в подвале любой страницы сайта. Если аналитика уже была разрешена, после ее отключения страница перезагружается, чтобы прекратить дальнейший сбор в текущем сеансе; ранее собранные данные в Яндекс.Метрике при этом автоматически не удаляются.</p>
<p>Для вопросов об обработке данных и отзыва согласия можно написать на <a href="mailto:info@prep-center.ru">info@prep-center.ru</a>. Согласие на аналитические cookie не заменяет согласие на обработку персональных данных, которое пользователь отдельно предоставляет при отправке заявки.</p>
<!-- prep-cookie-policy:end -->"""

# Replacement of the old generator's explicit no-script pixel insertion.
SCHEMA_OLD = '''    if "mc.yandex.ru/watch/100290924" not in result:
        pix = PIXEL + '<noscript><div><img src="https://mc.yandex.ru/watch/100290924" style="position:absolute;left:-9999px" alt=""></div></noscript>\\n'
        result, n = re.subn(r"<body\\b[^>]*>", lambda m: m.group(0) + "\\n" + pix, result, count=1, flags=re.I)
        if n != 1:
            raise AssertionError("Can't insert no-JS pixel on " + route)
'''
SCHEMA_NEW = '''    # No noscript tracking pixel: an opt-in choice is impossible without JS.
    if "mc.yandex.ru/watch/100290924" in result:
        raise AssertionError("Tracking pixel would bypass consent on " + route)
'''
SCHEMA_CHECK_OLD = '''    if not parsed.body.find("img", src="https://mc.yandex.ru/watch/100290924"):
        raise AssertionError("Missing no-script analytics fallback on " + route)
'''
SCHEMA_CHECK_NEW = '''    if parsed.body.find("img", src="https://mc.yandex.ru/watch/100290924"):
        raise AssertionError("Unexpected pre-consent tracking pixel on " + route)
'''


def page_path(route: str) -> Path:
    return ROOT / (route.strip("/") + "/index.html") if route != "/" else ROOT / "index.html"


def update_page(text: str, route: str) -> str:
    clean, pix_count = PIXEL_RE.subn("\n", text)
    if pix_count > 1:
        raise AssertionError("More than one tracking pixel on " + route)
    if "mc.yandex.ru/watch/100290924" in clean:
        raise AssertionError("Unmanaged Metika image on " + route)
    out, script_count = SHARED_JS_RE.subn(
        lambda m: m.group(1) + "?v=" + JS_VERSION + m.group(2),
        clean,
    )
    if script_count != 1:
        raise AssertionError("Expected one shared script on %s: %s" % (route, script_count))
    if "id=\"prep-cookie-banner\"" in out:
        raise AssertionError("Cookie dialog must be generated from shared JS on " + route)
    return out


def update_policy(text: str) -> str:
    text = re.sub(
        re.escape(POLICY_START) + r"[\s\S]*?" + re.escape(POLICY_END) + r"\s*",
        "", text,
    )
    if text.count(POLICY_ANCHOR) != 1:
        raise AssertionError("Cannot find unique end-of-policy anchor")
    return text.replace(POLICY_ANCHOR, POLICY_ANCHOR + "\n" + POLICY_CONTENT)


def update_builder(text: str) -> str:
    old = "shared-components.js?v=20261104"
    new = "shared-components.js?v=" + JS_VERSION
    if text.count(old) == 1:
        return text.replace(old, new)
    if text.count(new) == 1:
        return text
    raise AssertionError("Cannot find unique shared-components version in builder")


def update_schema_generator(text: str) -> str:
    if SCHEMA_OLD in text:
        text = text.replace(SCHEMA_OLD, SCHEMA_NEW)
    elif SCHEMA_NEW not in text:
        raise AssertionError("Unexpected schema source: pixel creation not recognized")
    if SCHEMA_CHECK_OLD in text:
        text = text.replace(SCHEMA_CHECK_OLD, SCHEMA_CHECK_NEW)
    elif SCHEMA_CHECK_NEW not in text:
        raise AssertionError("Unexpected schema source: pixel validation not recognized")
    if 'PIXEL = "<!-- prep-center-metrika-noscript -->"\n' in text:
        text = text.replace('PIXEL = "<!-- prep-center-metrika-noscript -->"\n', "")
    text = text.replace('"metrika_noscript": True', '"metrika_noscript": False')
    text = text.replace(
        '"Original counter 100290924 is unchanged; noscript fallback added.",',
        '"Counter 100290924 initializes only after analytics consent; no noscript pixel.",',
    )
    return text


def update_schema_report(text: str) -> str:
    obj = json.loads(text)
    for item in obj.get("pages", []):
        item["metrika_noscript"] = False
    old_note = "Original counter 100290924 is unchanged; noscript fallback added."
    new_note = "Counter 100290924 initializes only after analytics consent; no noscript pixel."
    obj["notes"] = [new_note if s == old_note else s for s in obj.get("notes", [])]
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    check = "--check" in sys.argv
    inventory = json.loads((ROOT / "restoration/page-inventory.json").read_text("utf-8"))
    routes = sorted({row["path"] for row in inventory if row.get("group") in GROUPS})
    if len(routes) != 45:
        raise AssertionError("Expected 45 pages, got %d" % len(routes))
    changes = []
    for route in routes:
        path = page_path(route)
        old = path.read_text("utf-8")
        new = update_page(old, route)
        if old != new:
            changes.append(str(path.relative_to(ROOT)))
            if not check:
                path.write_text(new, "utf-8")

    others = {
        "privacy-policy/index.html": update_policy,
        "scripts/build_components.py": update_builder,
        "scripts/restore_seo_schema.py": update_schema_generator,
        "reports/schema-restore-20261111.json": update_schema_report,
    }
    for rel, transform in others.items():
        path = ROOT / rel
        old = path.read_text("utf-8")
        new = transform(old)
        if new != old:
            changes.append(rel)
            if not check:
                path.write_text(new, "utf-8")

    # The check must pass only when all generated files have been committed.
    if check and changes:
        raise AssertionError("Stale cookie consent changes: " + ", ".join(changes))
    banner = (ROOT / "assets/cookie-consent.js").read_text("utf-8")
    shared = (ROOT / "assets/shared-components.js").read_text("utf-8")
    if "prep-cookie-consent-script" not in shared or "mc.yandex.ru/metrika/tag.js" in shared:
        raise AssertionError("Shared JS still initializes Metrika unconditionally")
    if any(token not in banner for token in (
        "prep-cookie-banner", "prep-cookie-settings",
        "prepcenter_cookie_consent_v1", "disableYaCounter",
        "Принять все", "Только необходимые", "metrika/tag.js",
    )):
        raise AssertionError("Cookie consent UI missing necessary functions")
    if check:
        policy = (ROOT / "privacy-policy/index.html").read_text("utf-8")
        if policy.count('id="cookies-and-analytics"') != 1:
            raise AssertionError("Missing unique privacy policy anchor")
    print(json.dumps({
        "mode": "check" if check else "write",
        "pages": len(routes), "changed_files": len(changes),
        "consent": "explicit opt-in, 180-day retention and revocation",
        "analytics_counter": 100290924, "noscript_pixels": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
