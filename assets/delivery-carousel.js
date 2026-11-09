(() => {
  const track = document.getElementById('delivery-track');
  const controls = track.nextElementSibling;
  const previous = controls.querySelector('.delivery-prev');
  const next = controls.querySelector('.delivery-next');
  const counter = controls.querySelector('.delivery-count');
  const last = track.children.length - 1;
  const current = () => Math.max(0, Math.min(last, Math.round(track.scrollLeft / track.clientWidth)));

  function updateControls() {
    const index = current();
    previous.disabled = index === 0;
    next.disabled = index === last;
    const status = `${index + 1} из ${last + 1}`;
    if (counter.textContent !== status) counter.textContent = status;
  }

  function moveBy(direction) {
    const index = Math.max(0, Math.min(last, current() + direction));
    track.scrollTo({ left: index * track.clientWidth });
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
