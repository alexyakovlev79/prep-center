/* No third-party map code is requested before the map approaches the viewport. */
(() => {
  const root = document.documentElement;
  const header = document.querySelector('.shared-header');
  const burger = header?.querySelector('.mobile-nav');
  let compact = window.scrollY > 15;
  function updateHeader() {
    if (!compact && window.scrollY > 15) compact = true;
    else if (compact && window.scrollY <= 4) compact = false;
    root.classList.toggle('header-compact', compact);
  }
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });
  window.addEventListener('pageshow', updateHeader);
  const closeMenus = () => header?.querySelectorAll('details[open]').forEach(d => d.open = false);
  header?.addEventListener('click', event => {
    if (event.target.closest('a')) closeMenus();
  });
  document.addEventListener('click', event => { if (header && !header.contains(event.target)) closeMenus(); });
  header?.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      const group = event.target.closest('details[open]');
      if (group) { group.open = false; group.querySelector('summary')?.focus(); }
    }
  });
  header?.querySelectorAll('.desktop-nav > .nav-root > li > details').forEach(group => {
    group.addEventListener('toggle', () => {
      if (group.open) header.querySelectorAll('.desktop-nav > .nav-root > li > details[open]').forEach(other => { if (other !== group) other.open = false; });
    });
  });
  const map = document.querySelector('[data-map-src]');
  if (!map) return;
  function loadMap() {
    if (map.querySelector('iframe')) return;
    const iframe = document.createElement('iframe');
    iframe.title = 'Преп-Центр — интерактивная Яндекс Карта';
    iframe.src = map.dataset.mapSrc;
    iframe.width = '560'; iframe.height = '290';
    iframe.referrerPolicy = 'strict-origin-when-cross-origin';
    iframe.allowFullscreen = true;
    iframe.addEventListener('load', () => map.classList.add('is-ready'), { once: true });
    map.append(iframe);
  }
  map.querySelector('button')?.addEventListener('click', loadMap);
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) { loadMap(); observer.disconnect(); }
    }, { rootMargin: '250px' });
    observer.observe(map);
  }
  // The footer remains normal document content across screen lock and bfcache restoration.
  window.addEventListener('pageshow', () => {
    if (map.getBoundingClientRect().top < window.innerHeight + 250) loadMap();
  });
})();

/* Contact form loader, shared by every restored page. */
(function loadPrepCenterLeadForm(){
  if(document.getElementById('prep-lead-form-script'))return;
  const style=document.createElement('link');
  style.rel='stylesheet';style.href='/assets/prep-lead-form.css?v=20261110-phone-border';
  document.head.appendChild(style);
  const boot=function(){
    if(document.getElementById('prep-lead-form-script'))return;
    const script=document.createElement('script');
    script.id='prep-lead-form-script';script.src='/assets/prep-lead-form.js?v=20261109';
    script.async=false;document.body.appendChild(script);
  };
  const config=document.createElement('script');
  config.src='/assets/prep-form-config.js?v=20261109';config.async=false;
  config.onload=boot;config.onerror=boot;document.head.appendChild(config);
})();
