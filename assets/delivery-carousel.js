(() => {
  const track = document.getElementById('delivery-track');
  const controls = track.nextElementSibling;
  const previous = controls.querySelector('.delivery-prev');
  const next = controls.querySelector('.delivery-next');
  const counter = controls.querySelector('.delivery-count');
  const count = track.children.length;
  const [firstCard, secondCard] = track.children;

  function position() {
    const step = secondCard.getBoundingClientRect().left - firstCard.getBoundingClientRect().left;
    const maxScroll = track.scrollWidth - track.clientWidth;
    const lastStart = Math.round(maxScroll / step);
    const index = Math.max(0, Math.min(lastStart, Math.round(track.scrollLeft / step)));
    return { step, maxScroll, lastStart, index };
  }

  function updateControls() {
    const { index, lastStart } = position();
    previous.disabled = index === 0;
    next.disabled = index === lastStart;
    const first = index + 1;
    const end = index + count - lastStart;
    const status = (first === end ? first : `${first}–${end}`) + ` из ${count}`;
    if (counter.textContent !== status) counter.textContent = status;
  }

  function moveBy(direction) {
    const { step, maxScroll, lastStart, index } = position();
    const target = Math.max(0, Math.min(lastStart, index + direction));
    track.scrollTo({ left: Math.min(maxScroll, target * step) });
  }

  previous.addEventListener('click', () => moveBy(-1));
  next.addEventListener('click', () => moveBy(1));
  track.addEventListener('scroll', updateControls, { passive: true });
  track.addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    moveBy(event.key === 'ArrowLeft' ? -1 : 1);
  });
  window.addEventListener('resize', updateControls);
  updateControls();
  controls.hidden = false;
})();
