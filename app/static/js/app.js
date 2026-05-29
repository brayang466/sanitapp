// SanitApp — utilidades front-end

document.querySelectorAll('.flash').forEach((el) => {
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transition = 'opacity 0.4s';
    setTimeout(() => el.remove(), 400);
  }, 5000);
});

function initSelectLista(root) {
  const hidden = root.querySelector('input[type="hidden"]');
  const trigger = root.querySelector('.select-lista-trigger');
  const panel = root.querySelector('.select-lista-panel');
  const search = root.querySelector('.select-lista-search');
  const textEl = root.querySelector('.select-lista-text');
  const options = Array.from(root.querySelectorAll('.select-lista-option'));
  const emptyMsg = root.querySelector('.select-lista-empty');
  const placeholder = trigger.dataset.placeholder || 'Seleccione';

  let highlighted = -1;

  function setValue(value) {
    hidden.value = value;
    textEl.textContent = value || placeholder;
    textEl.classList.toggle('is-placeholder', !value);
    options.forEach((li) => {
      li.classList.toggle('is-selected', li.dataset.value === value);
    });
  }

  function close() {
    root.classList.remove('is-open');
    trigger.setAttribute('aria-expanded', 'false');
    panel.hidden = true;
    highlighted = -1;
    options.forEach((li) => li.classList.remove('is-highlighted'));
  }

  function open() {
    root.classList.add('is-open');
    trigger.setAttribute('aria-expanded', 'true');
    panel.hidden = false;
    search.value = '';
    filter('');
    search.focus();
  }

  function filter(query) {
    const q = query.trim().toLowerCase();
    let visible = 0;
    options.forEach((li) => {
      const match = !q || li.dataset.value.toLowerCase().includes(q);
      li.hidden = !match;
      if (match) visible += 1;
    });
    if (emptyMsg) emptyMsg.hidden = visible > 0;
    highlighted = -1;
  }

  function selectOption(li) {
    setValue(li.dataset.value);
    close();
  }

  trigger.addEventListener('click', () => {
    if (root.classList.contains('is-open')) close();
    else open();
  });

  search.addEventListener('input', () => filter(search.value));

  search.addEventListener('keydown', (e) => {
    const visible = options.filter((li) => !li.hidden);
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      highlighted = Math.min(highlighted + 1, visible.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      highlighted = Math.max(highlighted - 1, 0);
    } else if (e.key === 'Enter' && highlighted >= 0) {
      e.preventDefault();
      selectOption(visible[highlighted]);
      return;
    } else if (e.key === 'Escape') {
      close();
      return;
    } else {
      return;
    }
    options.forEach((li) => li.classList.remove('is-highlighted'));
    if (visible[highlighted]) {
      visible[highlighted].classList.add('is-highlighted');
      visible[highlighted].scrollIntoView({ block: 'nearest' });
    }
  });

  options.forEach((li) => {
    li.addEventListener('click', () => selectOption(li));
  });

  document.addEventListener('click', (e) => {
    if (!root.contains(e.target)) close();
  });

  if (hidden.value) setValue(hidden.value);
}

document.querySelectorAll('[data-select-lista]').forEach(initSelectLista);
