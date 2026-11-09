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
  function move(direction) {
    const step = track.children[1].offsetLeft - track.children[0].offsetLeft;
    const end = track.scrollWidth - track.clientWidth;
    const current = track.scrollLeft;
    const target = direction < 0 && current < 2 ? end
      : direction > 0 && current > end - 2 ? 0
      : Math.max(0, Math.min(end, current + direction * step));
    track.scrollTo({
      left: target,
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',
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
  controls.hidden = false;
})();
