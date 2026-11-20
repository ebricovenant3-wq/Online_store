(() => {
  const search = document.querySelector('#library-search');
  const sort = document.querySelector('#library-sort');
  const productRoot = document.querySelector('#library-products');
  if (!search || !productRoot) return;

  const cards = [...productRoot.querySelectorAll('[data-library-product]')];
  const looks = [...document.querySelectorAll('[data-library-look]')];
  const looksSection = document.querySelector('[data-looks-section]');
  const piecesSection = document.querySelector('[data-pieces-section]');
  const empty = document.querySelector('#library-empty');
  const count = document.querySelector('#library-result-count');
  let mode = 'all';
  let category = 'all';

  function update() {
    const term = search.value.trim().toLocaleLowerCase();
    const visibleProducts = [];
    cards.forEach(card => {
      const textMatch = !term || card.dataset.search.includes(term);
      const categoryMatch = category === 'all'
        || card.dataset.category === category
        || (category === 'black' && /black|charcoal|dark/.test(card.dataset.colors || ''))
        || (category === 'light' && /white|cream|beige|grey|pink|light/.test(card.dataset.colors || ''));
      const visible = mode !== 'looks' && textMatch && categoryMatch;
      card.hidden = !visible;
      if (visible) visibleProducts.push(card);
    });

    visibleProducts.sort((a, b) => {
      if (sort.value === 'name') return a.dataset.name.localeCompare(b.dataset.name);
      if (sort.value === 'price-low') return Number(a.dataset.price) - Number(b.dataset.price);
      if (sort.value === 'price-high') return Number(b.dataset.price) - Number(a.dataset.price);
      return cards.indexOf(a) - cards.indexOf(b);
    }).forEach(card => productRoot.append(card));

    let visibleLooks = 0;
    looks.forEach(card => {
      const visible = mode !== 'pieces' && (!term || card.dataset.search.includes(term));
      card.hidden = !visible;
      if (visible) visibleLooks++;
    });
    looksSection.hidden = mode === 'pieces' || visibleLooks === 0;
    piecesSection.hidden = mode === 'looks';
    empty.hidden = visibleProducts.length > 0 || mode === 'looks';
    count.textContent = `${visibleProducts.length} ${visibleProducts.length === 1 ? 'PIECE' : 'PIECES'}`;
  }

  document.querySelectorAll('[data-mode]').forEach(button => {
    button.addEventListener('click', () => {
      mode = button.dataset.mode;
      document.querySelectorAll('[data-mode]').forEach(item => {
        const active = item === button;
        item.classList.toggle('is-active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      update();
    });
  });
  document.querySelectorAll('[data-category]').forEach(button => {
    button.addEventListener('click', () => {
      category = button.dataset.category;
      document.querySelectorAll('[data-category]').forEach(item => {
        const active = item === button;
        item.classList.toggle('is-active', active);
        item.setAttribute('aria-pressed', String(active));
      });
      update();
    });
  });
  search.addEventListener('input', update);
  sort.addEventListener('change', update);
  document.addEventListener('keydown', event => {
    if (event.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
      event.preventDefault();
      search.focus();
    }
  });
  update();
})();
