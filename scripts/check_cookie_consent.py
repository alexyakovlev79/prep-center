#!/usr/bin/env python3
"""Browser + file smoke tests for 45-page cookie choice and Yandex.Metrika opt-in."""
import json
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8765"
VERSION = "20261111-cookie-v1"
GROUPS = {
    "Услуги и категории", "Статьи и требования маркетплейсов",
    "Кейсы", "Основные страницы",
}


def assert_static():
    inv = json.loads((ROOT / "restoration/page-inventory.json").read_text("utf-8"))
    routes = sorted({row["path"] for row in inv if row.get("group") in GROUPS})
    assert len(routes) == 45
    for route in routes:
        path = ROOT / route.strip("/") / "index.html" if route != "/" else ROOT / "index.html"
        text = path.read_text("utf-8")
        soup = BeautifulSoup(text, "html.parser")
        shared = soup.select('script[src^="/assets/shared-components.js"]')
        assert len(shared) == 1, (route, "shared includes", len(shared))
        assert "v=" + VERSION in shared[0]["src"], (route, "stale version")
        assert "mc.yandex.ru/watch/100290924" not in text, (route, "pixel bypasses opt-in")
        assert soup.select_one('link[rel="canonical"]'), route
        assert soup.select_one('script[type="application/ld+json"]'), route
        assert len(soup.select('.shared-footer .footer-legal')) == 1, route
    privacy = (ROOT / "privacy-policy/index.html").read_text("utf-8")
    assert privacy.count('id="cookies-and-analytics"') == 1
    assert 'Яндекс.Метрику (счетчик № 100290924)' in privacy
    assert (ROOT / "assets/cookie-consent.css").exists()
    return routes


def test_behaviour():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        requests = []

        def metrika_stub(route):
            requests.append(route.request.url)
            route.fulfill(status=200, content_type="application/javascript",
                          body="window.__metrika_stub_loaded__ = true;")
        context.route("https://mc.yandex.ru/**", metrika_stub)

        page = context.new_page()
        page.goto(BASE + "/", wait_until="domcontentloaded")
        panel = page.locator("#prep-cookie-banner")
        panel.wait_for(state="visible", timeout=10000)
        page.wait_for_function(
            "getComputedStyle(document.querySelector('#prep-cookie-banner')).position === 'fixed'"
        )
        assert page.locator("#prep-cookie-banner").count() == 1
        assert not requests, "Metrika network request before consent"
        assert page.evaluate("typeof window.ym") == "undefined", "Metrika initialized before consent"
        assert page.evaluate("window.disableYaCounter100290924") is True
        assert page.locator(".prep-cookie-banner a[href='/privacy-policy/#cookies-and-analytics']").count() == 1

        page.get_by_role("button", name="Только необходимые").click()
        assert not panel.is_visible()
        assert page.evaluate("JSON.parse(localStorage.getItem('prepcenter_cookie_consent_v1')).analytics") is False
        page.reload(wait_until="domcontentloaded")
        page.locator("#prep-cookie-settings").wait_for()
        assert not panel.is_visible()
        assert not requests, "Rejected analytics was still requested"
        assert page.evaluate("window.disableYaCounter100290924") is True

        page.get_by_role("button", name="Настройки cookies").click()
        assert panel.is_visible()
        page.get_by_role("button", name="Принять все").click()
        page.wait_for_function("window.__prepCenterMetrikaInitialized === true")
        page.wait_for_function("document.querySelector('script[src=\"https://mc.yandex.ru/metrika/tag.js\"]') !== null")
        assert page.evaluate("window.disableYaCounter100290924") is False
        assert len(requests) == 1, ("unexpected count after opt-in", requests)
        assert page.evaluate("JSON.parse(localStorage.getItem('prepcenter_cookie_consent_v1')).analytics") is True
        results["desktop"] = "initial block, reject, persistence and opt-in verified"

        page.goto(BASE + "/about/", wait_until="domcontentloaded")
        page.locator("#prep-cookie-settings").wait_for()
        page.wait_for_function("window.__prepCenterMetrikaInitialized === true")
        assert page.locator("#prep-cookie-banner").is_hidden()
        assert len(requests) == 2, "Stored consent not reused for next page"

        page.get_by_role("button", name="Настройки cookies").click()
        assert panel.is_visible()
        with page.expect_navigation(wait_until="domcontentloaded"):
            page.get_by_role("button", name="Только необходимые").click()
        page.locator("#prep-cookie-settings").wait_for()
        assert page.evaluate("window.disableYaCounter100290924") is True
        assert page.evaluate("typeof window.ym") == "undefined"
        assert page.locator("#prep-cookie-banner").is_hidden()
        assert len(requests) == 2, "Tracking was requested after revocation"
        results["revoke"] = "previously active analytics stopped after page reload"

        mobile = browser.new_context(viewport={"width": 360, "height": 740},
                                     device_scale_factor=1, is_mobile=True,
                                     has_touch=True)
        mobile_requests = []
        mobile.route("https://mc.yandex.ru/**",
                     lambda route: (mobile_requests.append(route.request.url),
                                    route.fulfill(status=200, content_type="application/javascript",
                                                  body="window.__test_met = true;")))
        p2 = mobile.new_page()
        p2.goto(BASE + "/contacts/", wait_until="domcontentloaded")
        p2.locator("#prep-cookie-banner").wait_for(state="visible")
        p2.wait_for_function(
            "getComputedStyle(document.querySelector('#prep-cookie-banner')).position === 'fixed'"
        )
        box = p2.locator("#prep-cookie-banner").bounding_box()
        assert box and box["x"] >= -1 and box["y"] >= -1
        assert box["width"] <= 361 and box["x"] + box["width"] <= 361, box
        assert p2.locator(".prep-cookie-allow").bounding_box()["height"] >= 44
        assert p2.locator(".prep-cookie-decline").bounding_box()["height"] >= 44
        assert not mobile_requests
        p2.screenshot(path="/tmp/prep-cookie-mobile.png", full_page=False)
        results["mobile"] = "360px banner fits viewport and buttons >=44px"
        p2.get_by_role("button", name="Только необходимые").click()
        assert p2.locator("#prep-cookie-banner").is_hidden()

        page.screenshot(path="/tmp/prep-cookie-desktop.png", full_page=False)
        browser.close()
    return results


if __name__ == "__main__":
    pages = assert_static()
    result = test_behaviour()
    print(json.dumps({"pages": len(pages), "checks": result}, ensure_ascii=False, indent=2))
