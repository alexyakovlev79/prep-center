/* Prep-Center: explicit cookie/analytics preferences, single site-wide instance.
   Technical storage only before consent. Metrika 100290924 loads after opt-in.
   The consent UI is shared by all 45 restored pages. */
(function () {
  'use strict';
  if (window.__PREP_COOKIE_CONSENT_ACTIVE__) return;
  window.__PREP_COOKIE_CONSENT_ACTIVE__ = true;

  const COUNTER = 100290924;
  const DISABLE_KEY = 'disableYaCounter' + COUNTER;
  const STORE_KEY = 'prepcenter_cookie_consent_v1';
  const STORE_VERSION = 1;
  const MAX_AGE_MS = 180 * 24 * 60 * 60 * 1000;

  function storedChoice() {
    try {
      const data = JSON.parse(window.localStorage.getItem(STORE_KEY));
      if (!data || data.version !== STORE_VERSION || typeof data.analytics !== 'boolean') return null;
      const age = Date.now() - Date.parse(data.updatedAt || '');
      if (!Number.isFinite(age) || age < 0 || age > MAX_AGE_MS) return null;
      return data.analytics;
    } catch (_) {
      return null;
    }
  }

  function rememberChoice(allow) {
    try {
      window.localStorage.setItem(STORE_KEY, JSON.stringify({
        version: STORE_VERSION,
        analytics: allow,
        updatedAt: new Date().toISOString()
      }));
    } catch (_) {
      // Private browsing/storage errors must never block site navigation or forms.
    }
  }

  function startMetrika() {
    if (window.__prepCenterMetrikaInitialized) return;
    window[DISABLE_KEY] = false;
    window.__prepCenterMetrikaInitialized = true;
    (function (m, e, t, r, i, k, a) {
      m[i] = m[i] || function () {
        (m[i].a = m[i].a || []).push(arguments);
      };
      m[i].l = 1 * new Date();
      for (let j = 0; j < document.scripts.length; j++) {
        if (document.scripts[j].src === r) return;
      }
      k = e.createElement(t);
      a = e.getElementsByTagName(t)[0];
      k.async = true;
      k.src = r;
      a.parentNode.insertBefore(k, a);
    })(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js', 'ym');
    window.ym(COUNTER, 'init', {
      clickmap: true,
      trackLinks: true,
      accurateTrackBounce: true,
      webvisor: true
    });
  }

  // Set the official Yandex opt-out flag before any attempt at initialization.
  // An unknown choice is NOT consent. Old cookieAccepted is not silently migrated.
  let choice = storedChoice();
  if (choice !== true) {
    window[DISABLE_KEY] = true;
  } else {
    startMetrika();
  }

  const css = document.createElement('link');
  css.rel = 'stylesheet';
  css.href = '/assets/cookie-consent.css?v=20261111-v1';
  document.head.appendChild(css);

  function node(tag, cls, text) {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (text) el.textContent = text;
    return el;
  }

  const banner = node('section', 'prep-cookie-banner');
  banner.id = 'prep-cookie-banner';
  banner.setAttribute('role', 'region');
  banner.setAttribute('aria-label', 'Настройки файлов cookie');
  banner.setAttribute('aria-describedby', 'prep-cookie-description');

  const head = node('div', 'prep-cookie-head');
  const heading = node('h2', 'prep-cookie-title', 'Файлы cookie');
  heading.id = 'prep-cookie-title';
  const close = node('button', 'prep-cookie-close', '×');
  close.type = 'button';
  close.setAttribute('aria-label', 'Закрыть настройки файлов cookie');
  head.append(heading, close);

  const desc = node('p', 'prep-cookie-description');
  desc.id = 'prep-cookie-description';
  desc.append(document.createTextNode(
    'Необходимые данные используются для работы сайта и сохранения вашего выбора. ' +
    'С вашего разрешения подключаем Яндекс.Метрику и Вебвизор для анализа посещений. '
  ));
  const policy = node('a', 'prep-cookie-policy', 'Подробнее');
  policy.href = '/privacy-policy/#cookies-and-analytics';
  desc.appendChild(policy);

  const actions = node('div', 'prep-cookie-actions');
  const allowBtn = node('button', 'prep-cookie-allow', 'Принять все');
  allowBtn.type = 'button';
  const declineBtn = node('button', 'prep-cookie-decline', 'Только необходимые');
  declineBtn.type = 'button';
  actions.append(allowBtn, declineBtn);
  banner.append(head, desc, actions);

  function render() {
    // Without an explicit choice the banner must remain visible.
    banner.hidden = choice !== null;
    close.hidden = choice === null;
  }

  function choose(allow) {
    const alreadyInitialized = Boolean(window.__prepCenterMetrikaInitialized);
    rememberChoice(allow);
    choice = allow;
    render();
    if (allow) {
      startMetrika();
    } else {
      window[DISABLE_KEY] = true;
      // Metrika's in-memory runtime cannot be reliably unloaded mid-page.
      // Reload only after withdrawing an earlier active opt-in.
      if (alreadyInitialized) window.location.reload();
    }
  }

  allowBtn.addEventListener('click', () => choose(true));
  declineBtn.addEventListener('click', () => choose(false));
  close.addEventListener('click', () => {
    if (choice !== null) banner.hidden = true;
  });

  const footer = document.querySelector('.shared-footer .footer-legal');
  if (footer && !document.getElementById('prep-cookie-settings')) {
    const reopen = node('button', 'prep-cookie-settings', 'Настройки cookies');
    reopen.id = 'prep-cookie-settings';
    reopen.type = 'button';
    reopen.setAttribute('aria-controls', 'prep-cookie-banner');
    reopen.addEventListener('click', () => {
      banner.hidden = false;
      close.hidden = choice === null;
      heading.setAttribute('tabindex', '-1');
      heading.focus({ preventScroll: true });
    });
    footer.appendChild(reopen);
  }

  document.body.appendChild(banner);
  render();
  window.PrepCenterCookieConsent = Object.freeze({
    analyticsAllowed: () => choice === true,
    openSettings: () => {
      banner.hidden = false;
      close.hidden = choice === null;
      heading.setAttribute('tabindex', '-1');
      heading.focus({ preventScroll: true });
    }
  });
})();
