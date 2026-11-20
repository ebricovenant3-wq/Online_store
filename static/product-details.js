(() => {
  const products = window.RUNWAY_CATALOG?.products || {};
  const dialog = document.querySelector('#product-detail-dialog');
  if (!dialog) return;
  const image = dialog.querySelector('[data-detail-image]');
  const colors = dialog.querySelector('[data-detail-colors]');
  const sizes = dialog.querySelector('[data-detail-sizes]');
  const previewFilters = {
    'light grey': 'grayscale(.78) brightness(1.12)',
    grey: 'grayscale(.85) brightness(.92)',
    'heather grey': 'grayscale(.8) brightness(.9)',
    cream: 'sepia(.24) saturate(.78) brightness(1.03)',
    'dark brown': 'sepia(.78) saturate(1.7) brightness(.64)',
    pink: 'sepia(.42) saturate(2.4) hue-rotate(292deg) brightness(1.03)',
    black: 'grayscale(1) brightness(.48) contrast(1.18)',
    white: 'grayscale(1) brightness(1.24)',
    beige: 'sepia(.38) saturate(.82) brightness(.91)',
    charcoal: 'grayscale(1) brightness(.62)',
    'bottle green': 'sepia(.82) saturate(1.9) hue-rotate(73deg) brightness(.66)',
    red: 'sepia(1) saturate(2.8) hue-rotate(326deg) brightness(.9)'
  };

  try {
    window.RUNWAY_SELECTED_COLORS = JSON.parse(localStorage.getItem('runway-product-colors-v1') || '{}');
  } catch {
    window.RUNWAY_SELECTED_COLORS = {};
  }

  function applyProductColor(key, color) {
    if (!color) return;
    window.RUNWAY_SELECTED_COLORS[key] = color.hex;
    try {
      localStorage.setItem('runway-product-colors-v1', JSON.stringify(window.RUNWAY_SELECTED_COLORS));
    } catch {}
    const filter = previewFilters[color.name.toLowerCase()] || '';
    image.style.filter = filter;
    document.querySelectorAll(`[data-product="${key}"] .rw__media img, [data-product-detail="${key}"] img`).forEach(item => {
      item.style.filter = filter;
      item.dataset.previewColor = color.name;
    });
  }

  Object.entries(window.RUNWAY_SELECTED_COLORS).forEach(([key, hex]) => {
    const product = products[key];
    const color = product?.colors?.find(option => option.hex === hex);
    if (color) applyProductColor(key, color);
  });

  function openDetails(key) {
    const product = products[key];
    if (!product) return;
    dialog.dataset.productKey = key;
    dialog.querySelector('[data-detail-vendor]').textContent = product.vendor;
    dialog.querySelector('[data-detail-name]').textContent = product.name;
    dialog.querySelector('[data-detail-price]').textContent = `$${Number(product.price).toFixed(2)}`;
    dialog.querySelector('[data-detail-description]').textContent = product.description || 'Explore this piece from the runway collection.';
    image.src = product.image;
    image.alt = product.name;
    dialog.querySelector('[data-detail-link]').href = product.url;

    colors.replaceChildren();
    const selectedColor = product.colors?.find(color => color.hex === window.RUNWAY_SELECTED_COLORS[key]) || product.colors?.[0];
    (product.colors || []).forEach(color => {
      const index = product.colors.indexOf(color);
      const swatch = document.createElement('button');
      swatch.type = 'button';
      swatch.className = 'detail-swatch';
      swatch.style.setProperty('--swatch', color.hex);
      swatch.setAttribute('aria-label', color.name);
      swatch.setAttribute('aria-pressed', String(color === selectedColor));
      swatch.title = color.name;
      swatch.addEventListener('click', () => {
        colors.querySelectorAll('.detail-swatch').forEach(item => item.setAttribute('aria-pressed', 'false'));
        swatch.setAttribute('aria-pressed', 'true');
        dialog.querySelector('[data-detail-color-label]').textContent = color.name;
        applyProductColor(key, color);
      });
      colors.append(swatch);
    });
    dialog.querySelector('[data-detail-color-label]').textContent = selectedColor?.name || '';
    if (selectedColor) applyProductColor(key, selectedColor);
    dialog.querySelector('[data-detail-colors-wrap]').hidden = !product.colors?.length;

    sizes.replaceChildren();
    (product.sizes || []).forEach(size => {
      const chip = document.createElement('span');
      chip.className = 'detail-size';
      chip.textContent = size;
      sizes.append(chip);
    });
    dialog.querySelector('[data-detail-size-heading]').textContent = product.legend === 'Shoe size' ? 'Available shoe sizes' : 'Available sizes';
    dialog.showModal();
  }

  document.addEventListener('click', event => {
    const trigger = event.target.closest('[data-product-detail]');
    if (trigger) openDetails(trigger.dataset.productDetail);
    if (event.target.closest('[data-detail-close]')) dialog.close();
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });
})();
