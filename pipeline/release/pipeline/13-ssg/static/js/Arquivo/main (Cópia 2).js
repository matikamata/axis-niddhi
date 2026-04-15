/**
 * BRASILEIRINHO ENGINE — UNIFIED FRONTEND LOGIC V1.2
 */

(function () {
  'use strict';

  const LANG_KEY = 'br_lang';
  const THEME_KEY = 'br_theme';

  const THEMES = [
    { id: 'light', icon: '☀️' },
    { id: 'dark', icon: '🌙' },
    { id: 'colirio', icon: '🌿' },
    { id: 'sunset', icon: '🌅' },
    { id: 'sunrise', icon: '🏔️' }
  ];

  /* ---------- THEME ---------- */
  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) document.body.setAttribute('data-theme', saved);

    const container = document.getElementById('theme-controls');
    if (!container) return;

    container.innerHTML = '';
    THEMES.forEach(t => {
      const b = document.createElement('button');
      b.className = 'theme-btn';
      b.textContent = t.icon;
      b.onclick = () => {
        document.body.setAttribute('data-theme', t.id);
        localStorage.setItem(THEME_KEY, t.id);
      };
      container.appendChild(b);
    });
  }

  /* ---------- LANGUAGE ---------- */
  function initLang() {
    const radios = document.querySelectorAll('input[name="lang_switch"]');
    if (!radios.length) return;

    const saved = localStorage.getItem(LANG_KEY);
    if (saved) {
      const r = document.getElementById('lang-' + saved);
      if (r && !r.disabled) r.checked = true;
    }

    radios.forEach(r => {
      r.addEventListener('change', () => {
        if (r.checked) {
          localStorage.setItem(LANG_KEY, r.id.replace('lang-', ''));
        }
      });
    });
  }

  /* ---------- TOC ---------- */
  function generateTOC(contentId, listId) {
    const content = document.getElementById(contentId);
    const list = document.getElementById(listId);
    if (!content || !list) return;

    list.innerHTML = '';
    const h = content.querySelectorAll('h5');
    if (!h.length) {
      list.parentElement.style.display = 'none';
      return;
    }

    h.forEach((el, i) => {
      const id = `${contentId}-sec-${i}`;
      el.id = id;
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `#${id}`;
      a.textContent = el.textContent;
      li.appendChild(a);
      list.appendChild(li);
    });
  }

  /* ---------- INIT ---------- */
  document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.add('js-enabled');
    initTheme();
    initLang();
    generateTOC('content-en', 'toc-list-en');
    generateTOC('content-pt', 'toc-list-pt');
  });

})();

