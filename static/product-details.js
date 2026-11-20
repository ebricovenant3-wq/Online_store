(() => {
  const products = window.RUNWAY_CATALOG?.products || {};
  const dialog = document.querySelector('#product-detail-dialog');
  if (!dialog) return;
  const image = dialog.querySelector('[data-detail-image]');
  const colors = dialog.querySelector('[data-detail-colors]');
  const sizes = dialog.querySelector('[data-detail-sizes]');

  function openDetails(key) {
    const product = products[key];
    if (!product) return;
    dialog.querySelector('[data-detail-vendor]').textContent = product.vendor;
    dialog.querySelector('[data-detail-name]').textContent = product.name;
    dialog.querySelector('[data-detail-price]').textContent = `$${Number(product.price).toFixed(2)}`;
    dialog.querySelector('[data-detail-description]').textContent = product.description || 'Explore this piece from the runway collection.';
    image.src = product.image;
    image.alt = product.name;
    dialog.querySelector('[data-detail-link]').href = product.url;

    colors.replaceChildren();
    (product.colors || []).forEach((color, index) => {
      const swatch = document.createElement('button');
      swatch.type = 'button';
      swatch.className = 'detail-swatch';
      swatch.style.setProperty('--swatch', color.hex);
      swatch.setAttribute('aria-label', color.name);
      swatch.setAttribute('aria-pressed', String(index === 0));
      swatch.title = color.name;
      swatch.addEventListener('click', () => {
        colors.querySelectorAll('.detail-swatch').forEach(item => item.setAttribute('aria-pressed', 'false'));
        swatch.setAttribute('aria-pressed', 'true');
        dialog.querySelector('[data-detail-color-label]').textContent = color.name;
      });
      colors.append(swatch);
    });
    dialog.querySelector('[data-detail-color-label]').textContent = product.colors?.[0]?.name || '';
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
