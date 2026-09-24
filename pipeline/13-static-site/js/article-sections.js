/* Article-only heading discovery, outline and accessible collapse controls. */
(function () {
  'use strict';
  const selector = 'h2,h3,h4,h5,h6';
  const excluded = '.long-audio-layer,.derived-media-companion,.translation-notice,.mini-toc,.csl-tattoo,.print-review-banner,.print-video-marker,nav';
  const mounted = new WeakMap();
  const controllers = new WeakMap();
  const articles = [];

  function mount(contentId, listId) {
    const article = document.getElementById(contentId);
    const list = document.getElementById(listId);
    if (!article || !list || mounted.has(article)) return;
    const toc = list.closest('.toc-en,.toc-pt,.toc-es-419');
    const headings = Array.from(article.querySelectorAll(selector))
      .filter(h => !h.closest(excluded) && h.textContent.trim());
    list.replaceChildren();
    if (toc) toc.hidden = headings.length === 0;
    mounted.set(article, true);
    articles.push(article);
    if (!headings.length) return;

    const locale = article.lang || 'en-US';
    const words = locale === 'pt-BR' ? ['Expandir seção', 'Recolher seção']
      : locale === 'es-419' ? ['Expandir sección', 'Contraer sección'] : ['Expand section', 'Collapse section'];
    const key = 'axis-sections-v2:' + (article.dataset.pdpn || location.pathname) + ':' + contentId;
    let saved = {};
    try {
      const value = JSON.parse(sessionStorage.getItem(key) || '{}');
      if (value && typeof value === 'object' && !Array.isArray(value)) saved = value;
    } catch (_) { /* Storage is optional. */ }
    let oldH5Index = 0;
    const entries = headings.map((heading, index) => {
      heading.classList.add('article-section-heading');
      const label = heading.textContent.trim();
      const level = Number(heading.tagName.slice(1));
      const base = heading.tagName === 'H5' ? contentId + '-sec-' + oldH5Index++
        : contentId + '-heading-' + index;
      let id = base;
      let suffix = 1;
      while (document.getElementById(id) && document.getElementById(id) !== heading) id = base + '-' + suffix++;
      // Keep original heading IDs; scoped aliases avoid cross-language collisions.
      if (heading.id !== id) {
        const anchor = document.createElement('span');
        anchor.id = id;
        anchor.className = 'article-section-anchor';
        anchor.setAttribute('aria-hidden', 'true');
        heading.prepend(anchor);
      }
      return { heading, label, level, id };
    });
    const levels = new Map(entries.map(e => [e.heading, e.level]));

    // Process inner/later sections first. Never split an existing DOM container
    // or absorb a same/higher heading hidden inside a following container.
    entries.slice().reverse().forEach(entry => {
      const nodes = [];
      let node = entry.heading.nextSibling;
      while (node) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          if (node.matches(excluded) || node.querySelector(excluded)) break;
          const contained = [node, ...node.querySelectorAll(selector)];
          if (contained.some(h => levels.has(h) && levels.get(h) <= entry.level)) break;
        }
        nodes.push(node);
        node = node.nextSibling;
      }
      if (!nodes.some(n => n.nodeType === Node.ELEMENT_NODE || n.textContent.trim())) return;
      const wrapper = document.createElement('div');
      wrapper.className = 'section-content';
      let wrapperId = entry.id + '-body';
      while (document.getElementById(wrapperId)) wrapperId += '-section';
      wrapper.id = wrapperId;
      entry.heading.after(wrapper);
      nodes.forEach(n => wrapper.appendChild(n));
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'section-toggle';
      button.setAttribute('aria-controls', wrapper.id);
      const icon = document.createElement('span');
      icon.setAttribute('aria-hidden', 'true');
      icon.textContent = '\u25be';
      button.appendChild(icon);
      entry.heading.appendChild(button);
      const storageId = entry.id + ':' + entry.label;
      function setCollapsed(collapsed, persist) {
        wrapper.hidden = collapsed;
        wrapper.classList.toggle('collapsed', collapsed);
        entry.heading.classList.toggle('collapsed', collapsed);
        button.setAttribute('aria-expanded', String(!collapsed));
        button.setAttribute('aria-label', words[collapsed ? 0 : 1] + ': ' + entry.label);
        button.title = words[collapsed ? 0 : 1];
        if (persist) {
          saved[storageId] = collapsed;
          try { sessionStorage.setItem(key, JSON.stringify(saved)); } catch (_) { /* Optional. */ }
        }
      }
      controllers.set(wrapper, () => setCollapsed(false, true));
      controllers.set(entry.heading, () => setCollapsed(false, true));
      setCollapsed(saved[storageId] === true, false);
      button.addEventListener('click', () => setCollapsed(!wrapper.hidden, true));
      entry.heading.addEventListener('click', event => {
        if (!event.target.closest('a,button,input,select,textarea,[role="button"]')) setCollapsed(!wrapper.hidden, true);
      });
    });

    const stack = [];
    entries.forEach(entry => {
      while (stack.length && stack[stack.length - 1].level >= entry.level) stack.pop();
      let parent = list;
      if (stack.length) {
        const ancestor = stack[stack.length - 1];
        if (!ancestor.children) {
          ancestor.children = document.createElement('ul');
          ancestor.item.appendChild(ancestor.children);
        }
        parent = ancestor.children;
      }
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = '#' + entry.id;
      link.textContent = entry.label;
      link.addEventListener('click', () => reveal(entry.heading, article));
      item.appendChild(link);
      parent.appendChild(item);
      stack.push({ level: entry.level, item });
    });
  }

  function reveal(target, article) {
    for (let node = target; node && node !== article; node = node.parentElement) {
      const expand = controllers.get(node);
      if (expand) expand();
    }
    const radio = document.getElementById(article.id.replace('content-', 'lang-'));
    if (radio && !radio.disabled && !radio.checked) {
      radio.checked = true;
      radio.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }

  function revealHash() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    if (!id) return;
    const checked = document.querySelector('input[name="lang_switch"]:checked');
    const active = checked && checked.id.replace('lang-', 'content-');
    const preferred = articles.slice().sort((a, b) => Number(b.id === active) - Number(a.id === active));
    for (const article of preferred) {
      const target = Array.from(article.querySelectorAll('[id]')).find(n => n.id === id);
      if (target) {
        reveal(target, article);
        target.scrollIntoView();
        return;
      }
    }
  }

  window.addEventListener('hashchange', revealHash);
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || event.defaultPrevented || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const url = new URL(link.href, location.href);
    if (url.origin === location.origin && url.pathname === location.pathname &&
        url.search === location.search && url.hash) requestAnimationFrame(revealHash);
  });
  window.AxisArticleSections = { mount, revealHash };
})();
