(() => {
  const hero = document.querySelector('[data-featured-look]');
  const cards = [...document.querySelectorAll('.dashboard-look')];
  if (!hero || !cards.length) return;

  const image = hero.querySelector('[data-featured-image]');
  const number = hero.querySelector('[data-featured-number]');
  const name = hero.querySelector('[data-featured-name]');
  const autoButton = hero.querySelector('[data-feature-auto]');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let index = 0;
  let rotating = !reducedMotion;
  let interval;

  function showLook(next) {
    index = (next + cards.length) % cards.length;
    const card = cards[index];
    const photo = card.querySelector('img');
    const title = card.querySelector('h3').textContent.trim();
    hero.classList.add('is-changing');
    setTimeout(() => {
      image.src = photo.src;
      image.alt = title;
      name.textContent = title;
      number.textContent = `LOOK 0${index + 1} / 0${cards.length}`;
      hero.classList.remove('is-changing');
    }, reducedMotion ? 0 : 180);
  }

  function setRotation(active) {
    rotating = active && !reducedMotion;
    autoButton.setAttribute('aria-pressed', String(rotating));
    hero.dataset.spinning = String(rotating);
    clearInterval(interval);
    if (rotating) interval = setInterval(() => showLook(index + 1), 5000);
  }

  hero.querySelector('[data-feature-prev]').addEventListener('click', () => showLook(index - 1));
  hero.querySelector('[data-feature-next]').addEventListener('click', () => showLook(index + 1));
  autoButton.addEventListener('click', () => setRotation(!rotating));
  hero.addEventListener('mouseenter', () => clearInterval(interval));
  hero.addEventListener('mouseleave', () => { if (rotating) interval = setInterval(() => showLook(index + 1), 5000); });

  document.querySelectorAll('[data-tilt]').forEach(card => {
    card.addEventListener('pointermove', event => {
      if (event.pointerType !== 'mouse' || reducedMotion) return;
      const rect = card.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width;
      const y = (event.clientY - rect.top) / rect.height;
      card.style.setProperty('--tilt-x', `${(0.5 - y) * 9}deg`);
      card.style.setProperty('--tilt-y', `${(x - 0.5) * 11}deg`);
      card.style.setProperty('--shine-x', `${x * 100}%`);
      card.style.setProperty('--shine-y', `${y * 100}%`);
      card.classList.add('is-tilting');
    });
    card.addEventListener('pointerleave', () => {
      card.style.setProperty('--tilt-x', '0deg');
      card.style.setProperty('--tilt-y', '0deg');
      card.classList.remove('is-tilting');
    });
  });
  setRotation(rotating);
})();
