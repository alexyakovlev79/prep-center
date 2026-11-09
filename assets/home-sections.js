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
  const cards = [...track.children];
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
      if (height && track.style.height !== size) track.style.height = size;
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
