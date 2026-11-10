(() => {
  const reviewButton = document.getElementById('show-reviews');
  const moreReviews = document.getElementById('more-reviews');
  reviewButton.hidden = false;
  reviewButton.addEventListener('click', () => {
    const expanding = moreReviews.hidden;
    const top = reviewButton.getBoundingClientRect().top;
    moreReviews.hidden = !expanding;
    reviewButton.setAttribute('aria-expanded', String(expanding));
    reviewButton.textContent = expanding ? 'Свернуть отзывы' : 'Показать все отзывы';

    if (!expanding) {
      window.scrollBy({ top: reviewButton.getBoundingClientRect().top - top, behavior: 'instant' });
    }
  });

  const track = document.getElementById('feature-track');
  const controls = track.nextElementSibling;
  const cards = [...track.querySelectorAll('.home-feature-content')];
  let pendingHeight = 0;

  function updateHeight() {
    if (pendingHeight) return;
    pendingHeight = requestAnimationFrame(() => {
      pendingHeight = 0;
      const { left, right } = track.getBoundingClientRect();
      if (right <= left) return;
      const height = cards.reduce((largest, card) => {
        const bounds = card.getBoundingClientRect();
        return bounds.right > left + 1 && bounds.left < right - 1
          ? Math.max(largest, bounds.height)
          : largest;
      }, 0);
      const size = `${Math.ceil(height)}px`;
      if (height && track.style.getPropertyValue('--feature-row-height') !== size) {
        track.style.setProperty('--feature-row-height', size);
      }
      if (track.scrollTop) track.scrollTop = 0;
    });
  }

  function move(direction) {
    const step = track.children[1].offsetLeft - track.children[0].offsetLeft;
    const end = track.scrollWidth - track.clientWidth;
    const current = track.scrollLeft;
    const wrap = direction < 0 ? current < 2 : current > end - 2;
    const target = wrap ? (direction < 0 ? end : 0)
      : Math.max(0, Math.min(end, current + direction * step));
    track.scrollTo({
      left: target,
      behavior: wrap || window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',
    });
  }

  controls.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', () => move(Number(button.dataset.direction)));
  });
  track.addEventListener('keydown', (event) => {
    if (event.target !== track || (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight')) return;
    event.preventDefault();
    move(event.key === 'ArrowRight' ? 1 : -1);
  });
  track.parentElement.dataset.ready = '';
  controls.hidden = false;
  track.addEventListener('scroll', updateHeight, { passive: true });
  const layout = new ResizeObserver(updateHeight);
  layout.observe(track);
  cards.forEach(card => layout.observe(card));
  updateHeight();
})();

/* Six customer cases: swipe on phones, natural height per selected slide. */
(() => {
  const track = document.getElementById('home-case-track');
  const controls = track?.nextElementSibling;
  if (!track || !controls) return;
  const cards = Array.from(track.children);
  if (cards.length < 2) return;
  const previous = controls.querySelector('.home-case-prev');
  const next = controls.querySelector('.home-case-next');
  const counter = controls.querySelector('.home-case-count');
  const mobile = window.matchMedia('(max-width:700px)');

  function getPosition() {
    const step = cards[1].offsetLeft - cards[0].offsetLeft;
    const limit = Math.max(0, track.scrollWidth - track.clientWidth);
    const index = step ? Math.max(0, Math.min(cards.length - 1, Math.round(track.scrollLeft / step))) : 0;
    return { step, limit, index };
  }

  function update() {
    if (!mobile.matches) {
      track.style.removeProperty('height');
      controls.hidden = true;
      return;
    }
    const { index } = getPosition();
    const height = Math.ceil(cards[index].getBoundingClientRect().height);
    if (height > 0 && track.style.height !== `${height}px`) track.style.height = `${height}px`;
    previous.disabled = index === 0;
    next.disabled = index === cards.length - 1;
    const label = `${index + 1} из ${cards.length}`;
    if (counter.textContent !== label) counter.textContent = label;
    controls.hidden = false;
  }

  function move(direction) {
    const { step, limit, index } = getPosition();
    const target = Math.max(0, Math.min(cards.length - 1, index + direction));
    track.scrollTo({
      left: Math.min(limit, target * step),
      behavior: window.matchMedia('(prefers-reduced-motion:reduce)').matches ? 'instant' : 'smooth'
    });
  }

  previous.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  track.addEventListener('scroll', update, { passive:true });
  track.addEventListener('keydown', event => {
    if (event.target !== track || !['ArrowLeft','ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    move(event.key === 'ArrowLeft' ? -1 : 1);
  });
  window.addEventListener('resize', update);
  window.addEventListener('load', update, { once:true });
  if (document.fonts) document.fonts.ready.then(update);
  if ('ResizeObserver' in window) {
    const observer = new ResizeObserver(update);
    cards.forEach(card => observer.observe(card));
  }
  update();
})();
