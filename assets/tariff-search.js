(() => {
  const input = document.getElementById('tariff-search');
  if (!input) return;
  const groups = Array.from(document.querySelectorAll('details.tariff-category'));
  const count = document.getElementById('tariff-count');
  const empty = document.getElementById('tariff-empty');
  const normalize = value => value.toLocaleLowerCase('ru').replaceAll('ё', 'е').replace(/\s+/g, ' ').trim();
  const total = groups.reduce((n, group) => n + group.querySelectorAll('.tariff-row').length, 0);
  let beforeSearch = null;
  const plural = n => n % 10 === 1 && n % 100 !== 11 ? 'тариф' : [2,3,4].includes(n % 10) && ![12,13,14].includes(n % 100) ? 'тарифа' : 'тарифов';
  function search() {
    const query = normalize(input.value);
    if (query && beforeSearch === null) beforeSearch = groups.map(group => group.open);
    let found = 0;
    groups.forEach((group, i) => {
      const rows = Array.from(group.querySelectorAll('.tariff-row'));
      let matches = 0;
      rows.forEach(row => {
        row.hidden = !!query && !normalize(row.dataset.search).includes(query);
        if (!row.hidden) matches++;
      });
      group.hidden = matches === 0;
      if (query) group.open = matches > 0;
      else if (beforeSearch !== null) group.open = beforeSearch[i];
      const badge = group.querySelector('.tariff-category__count');
      badge.textContent = query ? matches + ' из ' + rows.length : rows.length + ' ' + plural(rows.length);
      found += matches;
    });
    if (!query) beforeSearch = null;
    count.textContent = query ? 'Найдено: ' + found + ' из ' + total : 'Всего ' + total + ' тарифа. Выберите раздел, чтобы посмотреть услуги и описания.';
    empty.hidden = found !== 0;
  }
  input.addEventListener('input', search);
  input.addEventListener('search', search);
  search();

  // A tariff URL can now point to an individual row. Tariff sections are
  // collapsed by default, so expand the matching section before scrolling.
  function openLinkedTariff() {
    const match = /^#tariff-(PC-TAR-\\d{3})$/i.exec(window.location.hash);
    if (!match) return;
    const row = document.getElementById('tariff-' + match[1].toUpperCase());
    if (!row) return;
    if (input.value || row.hidden) {
      input.value = '';
      search();
    }
    const section = row.closest('details.tariff-category');
    if (section) {
      section.hidden = false;
      section.open = true;
    }
    window.requestAnimationFrame(() => row.scrollIntoView({ block: 'center' }));
  }

  window.addEventListener('hashchange', openLinkedTariff);
  openLinkedTariff();
})();
