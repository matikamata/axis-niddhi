/* pipeline/13-ssg/static/js/main.js */

/**
 * AXIS-NIDDHI ENGINE — UNIFIED FRONTEND LOGIC V1.5.1
 * [20260420] SPRINT O: initPronunciation() — lazy audio loading (preload='none', src on click)
 * [20260309] PATCH-B2: initPronunciation() — NFC normalization + explicit console logging
 * [20260309] PATCH-B:  initPronunciation() — dual-schema manifest loader
 * [20260223] Added: Offline Search UI (Sprint 9)
 * [20260222] Added: initPronunciation() — click-to-play Pāli audio affordance
 */



// [FF-012c] View Mode Toggle — global so onclick="" in HTML can reach it
// Sets data-view on body for CSS-driven mode switching
function setViewMode(mode) {
  const reader      = document.getElementById('view-reader');
  const comparative = document.getElementById('view-comparative');
  if (!reader || !comparative) return;

  const isComparative = (mode === 'comparative');
  reader.hidden      =  isComparative;
  comparative.hidden = !isComparative;

  // Update button states (works with any number of .view-btn elements)
  document.querySelectorAll('.view-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === mode);
  });

  // data-view on body enables CSS-only per-mode rules
  document.body.setAttribute('data-view', mode);

  try { localStorage.setItem('axis-view-mode', mode); } catch(e) {}
}


// [FF-013] Labz toggle — acesso ao Stardust Overworld
// Ativa tema experimental + banner informativo para revisores
function toggleLabz() {
  const isActive = document.body.getAttribute('data-theme') === 'stardust';
  const btn    = document.getElementById('labz-btn');
  const banner = document.getElementById('labz-banner');
  const THEME_KEY = 'br_theme';

  if (isActive) {
    // Restaurar tema anterior
    const prev = localStorage.getItem('axis-theme-pre-labz') || 'dark';
    document.body.setAttribute('data-theme', prev);
    localStorage.setItem(THEME_KEY, prev);
    localStorage.setItem('axis-niddhi-theme', prev);
    localStorage.removeItem('axis-theme-pre-labz');
    btn    && btn.classList.remove('labz-active');
    banner && banner.classList.remove('visible');
  } else {
    // Salvar tema atual e ativar stardust
    const prev = document.body.getAttribute('data-theme') || 'dark';
    localStorage.setItem('axis-theme-pre-labz', prev);
    document.body.setAttribute('data-theme', 'stardust');
    localStorage.setItem('axis-niddhi-theme', 'stardust');
    btn    && btn.classList.add('labz-active');
    banner && banner.classList.add('visible');
    console.log('⚗️ LABZ: Stardust Overworld activated. Welcome to the terminal.');
  }
}

(function () {
  'use strict';

  const LANG_KEY = 'br_lang';
  const THEME_KEY = 'br_theme';

  const THEMES = [
    { id: 'light', icon: '🏔️' },
    { id: 'dark', icon: '🌙' },
    { id: 'sunrise', icon: '☀️' },
    { id: 'colirio', icon: '🌿' },
    { id: 'sunset', icon: '🌅' }
    // stardust é gerido pelo toggleLabz() — não aparece no theme switcher normal
  ];

  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    const labzState = localStorage.getItem('axis-niddhi-theme');
    if (labzState === 'stardust') {
      document.body.setAttribute('data-theme', 'stardust');
      // [FF-013] Restore labz button state if stardust was active
      const btn = document.getElementById('labz-btn');
      const banner = document.getElementById('labz-banner');
      btn    && btn.classList.add('labz-active');
      banner && banner.classList.add('visible');
    } else if (saved) {
      document.body.setAttribute('data-theme', saved);
    }

    const container = document.getElementById('theme-controls');
    if (!container) return;

    container.innerHTML = '';
    THEMES.forEach(t => {
      const b = document.createElement('button');
      b.className = 'theme-btn';
      b.textContent = t.icon;
      b.onclick = () => {
        const isLabzActive = document.body.getAttribute('data-theme') === 'stardust';
        if (isLabzActive) {
          // Em LABZ, trocar tema ajusta o "tema de saída" sem desligar o stardust.
          localStorage.setItem('axis-theme-pre-labz', t.id);
        } else {
          document.body.setAttribute('data-theme', t.id);
          localStorage.setItem('axis-niddhi-theme', t.id);
        }
        localStorage.setItem(THEME_KEY, t.id);
      };
      container.appendChild(b);
    });
  }

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

  function initAccordion() {
    const sections = document.querySelectorAll('.library-section');
    sections.forEach(section => {
      const h2 = section.querySelector('h2');
      if (!h2) return;

      h2.addEventListener('click', () => {
        h2.classList.toggle('active');
        const list = section.querySelector('.accordion-content');
        if (list) {
          if (h2.classList.contains('active')) {
            list.style.maxHeight = list.scrollHeight + 'px';
            const icon = h2.querySelector('.toggle-icon');
            if(icon) icon.textContent = '▼';
          } else {
            list.style.maxHeight = '0px';
            const icon = h2.querySelector('.toggle-icon');
            if(icon) icon.textContent = '▶';
          }
        }
      });
    });

    // SPRINT 14: Auto-expand section if hash matches
    function handleHash() {
      const hash = window.location.hash;
      if (!hash) return;
      const target = document.querySelector(hash);
      if (target && target.classList.contains('library-section')) {
        const list = document.getElementById('all-sections-list');
        const toggle = document.getElementById('section-list-toggle');
        if (list && toggle) {
          list.hidden = false;
          toggle.setAttribute('aria-expanded', 'true');
          toggle.textContent = 'Hide all sections / Ocultar seções';
        }

        const h2 = target.querySelector('h2');
        if (h2) {
          h2.classList.add('active');
          const list = target.querySelector('.accordion-content');
          if (list) {
            // Give time for layout calc
            setTimeout(() => { list.style.maxHeight = list.scrollHeight + 'px'; }, 50);
            const icon = h2.querySelector('.toggle-icon');
            if(icon) icon.textContent = '▼';
          }
        }
        // Smooth scroll to ensure visibility
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    window.addEventListener('hashchange', handleHash);
    handleHash(); // Run on load
  }

  function initSectionListToggle() {
    const list = document.getElementById('all-sections-list');
    const toggle = document.getElementById('section-list-toggle');
    if (!list || !toggle) return;

    document.body.classList.add('js-section-list-collapsed');
    const hashTarget = window.location.hash ? document.querySelector(window.location.hash) : null;
    const startsOpen = !!(hashTarget && hashTarget.classList.contains('library-section'));
    list.hidden = !startsOpen;
    toggle.setAttribute('aria-expanded', String(startsOpen));
    toggle.textContent = startsOpen
      ? 'Hide all sections / Ocultar seções'
      : 'View all sections / Ver todas as seções';

    toggle.addEventListener('click', function() {
      const shouldShow = list.hidden;
      list.hidden = !shouldShow;
      toggle.setAttribute('aria-expanded', String(shouldShow));
      toggle.textContent = shouldShow
        ? 'Hide all sections / Ocultar seções'
        : 'View all sections / Ver todas as seções';

      if (shouldShow) {
        list.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  }

  function initArticleLinkTargets() {
    const articlePath = /(?:^|\/)pages\/[A-Z]{2}\.[A-Z]{2}\.\d{3}\/(?:index\.html)?$/i;
    document.querySelectorAll('a[href]').forEach(link => {
      const href = link.getAttribute('href') || '';
      if (!articlePath.test(href)) return;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
    });
  }

  function initInlineSectionReveal() {
    const grid = document.querySelector('.section-grid');
    const panel = document.getElementById('inline-section-panel');
    if (!grid || !panel) return;

    const cards = Array.from(grid.querySelectorAll('.section-card[href^="#section-"]'));
    if (!cards.length) return;

    function closePanel() {
      panel.hidden = true;
      panel.innerHTML = '';
      cards.forEach(card => card.classList.remove('active'));
    }

    function getLastCardInRow(card) {
      const rowTop = card.offsetTop;
      let lastInRow = card;
      cards.forEach(item => {
        if (item.offsetTop === rowTop) lastInRow = item;
      });
      return lastInRow;
    }

    grid.addEventListener('click', function(event) {
      const card = event.target.closest('.section-card[href^="#section-"]');
      if (!card || !grid.contains(card)) return;

      const targetId = card.getAttribute('href');
      const source = targetId ? document.querySelector(targetId) : null;
      if (!source || !source.classList.contains('library-section')) return;

      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();

      const lastInRow = getLastCardInRow(card);
      if (lastInRow && lastInRow.nextElementSibling !== panel) {
        lastInRow.insertAdjacentElement('afterend', panel);
      }

      const clone = source.cloneNode(true);
      clone.removeAttribute('id');
      clone.classList.add('inline-section-clone');
      clone.querySelectorAll('[id]').forEach(el => {
        el.id = `inline-${el.id}`;
      });

      const h2 = clone.querySelector('h2');
      const list = clone.querySelector('.accordion-content');
      const icon = clone.querySelector('.toggle-icon');
      if (h2) h2.classList.add('active');
      if (list) list.style.maxHeight = 'none';
      if (icon) icon.textContent = '▼';

      const header = document.createElement('div');
      header.className = 'inline-section-panel-header';

      const close = document.createElement('button');
      close.type = 'button';
      close.className = 'inline-section-close';
      close.textContent = 'Close / Fechar';
      close.addEventListener('click', closePanel);

      header.appendChild(close);
      panel.innerHTML = '';
      panel.appendChild(header);
      panel.appendChild(clone);
      panel.hidden = false;

      cards.forEach(item => item.classList.toggle('active', item === card));
      panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, true);
  }

  function getRootPath() {
    var parts = window.location.pathname.split('/').filter(p => p !== '');
    var pagesIndex = parts.indexOf('pages');

    // Root pages (index/archive) always load side assets from current dir.
    if (pagesIndex === -1) return './';

    // Post URLs can be:
    // - /pages/PDPN/index.html
    // - /pages/PDPN/
    // - /axis-niddhi/pages/PDPN/index.html (GitHub Pages project path)
    var lastPart = parts[parts.length - 1] || '';
    var isPdpn = /^[A-Z]{2}\.[A-Z]{2}\.\d{3}$/i.test(lastPart);
    var isFile = lastPart.indexOf('.') !== -1 && !isPdpn;

    // Depth from current page to site root (where search_index/pronunciation_manifest live).
    var depth = isFile
      ? (parts.length - pagesIndex - 1)
      : (parts.length - pagesIndex);

    if (depth <= 0) return './';
    return '../'.repeat(depth);
  }

  function initPronunciation() {
    var terms = document.querySelectorAll('.term-highlight');
    if (!terms.length) return;

    var EXTERNAL_AUDIO_BASE = 'https://puredhamma.net/wp-content/uploads/';
    var root = getRootPath();
    var manifestUrl = root + 'pronunciation_manifest.json';
    
    function loadManifest(url, isRetry) {
      console.log('[Pronunciation] Attempting manifest load:', url);
      fetch(url)
        .then(function(r) {
          if (!r.ok) throw new Error('HTTP ' + r.status);
          return r.json();
        })
        .then(function(manifest) {
          setupAudio(manifest, root);
        })
        .catch(function(err) {
          console.warn('[Pronunciation] Load failed for ' + url + ':', err);
          if (!isRetry) {
            // Fallback bound to current site root (works for /axis-niddhi/ too).
            var fallbackUrl = new URL(root + 'pronunciation_manifest.json', window.location.href).toString();
            if (fallbackUrl !== url) {
              loadManifest(fallbackUrl, true);
            }
          }
        });
    }

    function setupAudio(manifest, currentRoot) {
      function buildExternalAudioUrl(pathLike) {
        if (!pathLike) return null;
        var m = String(pathLike).match(/assets\/audio\/en-US\/([^?#]+)/i);
        if (!m || !m[1]) return null;
        var filename = m[1].split('/').pop();
        if (!filename) return null;
        try {
          filename = decodeURIComponent(filename);
        } catch (_) {}
        return EXTERNAL_AUDIO_BASE + encodeURIComponent(filename);
      }

      function resolveAudioPath(termKey) {
        var key = termKey.normalize ? termKey.normalize('NFC') : termKey;
        var path = null;

        if (manifest.terms) {
          var entry = manifest.terms[key] || manifest.terms[termKey];
          if (entry && entry.available && entry.mp3) {
            path = 'assets/audio/en-US/' + entry.mp3;
          }
        } else {
          path = manifest[key] || manifest[termKey];
        }

        if (!path) return null;
        // Externalized oversized artifacts can be absolute URLs.
        if (/^(?:https?:)?\/\//i.test(path)) return path;
        // Site-root absolute path.
        if (path.startsWith('/')) return path;
        // Default to relative resolution
        return currentRoot + path;
      }

      var activated = 0;
      terms.forEach(function(el) {
        var termKey = el.getAttribute('data-term');
        if (!termKey) return;

        var audioPath = resolveAudioPath(termKey);
        if (!audioPath) return;

        el.classList.add('has-audio');
        activated++;

        el.addEventListener('click', function(e) {
          e.preventDefault();
          // [SPRINT O] Lazy loading + robust fallback chain (relative -> absolute -> external canonical URL).
          var candidates = [audioPath];
          if (!/^(?:https?:)?\/\//i.test(audioPath) && !audioPath.startsWith('/')) {
            candidates.push(new URL(audioPath, window.location.href).toString());
          }
          var externalUrl = buildExternalAudioUrl(audioPath);
          if (externalUrl && candidates.indexOf(externalUrl) === -1) {
            candidates.push(externalUrl);
          }

          function tryPlay(index) {
            if (index >= candidates.length) return;
            var src = candidates[index];
            var audio = new Audio();
            audio.preload = 'none';
            audio.src = src;
            audio.play().catch(function(err) {
              console.warn('[Pronunciation] Play failed:', src, err);
              tryPlay(index + 1);
            });
          }

          tryPlay(0);
        });
      });
      console.log('[Pronunciation] Ready. Active terms:', activated);
    }

    loadManifest(manifestUrl, false);
  }

  function initSearch() {
    const input = document.getElementById('search-input');
    const resultsContainer = document.getElementById('search-results');
    if (!input || !resultsContainer) return;

    let index = null;
    let root = getRootPath();

    // [FF-010] Unicode normalization: desana == desanā == Desanā
    function normalize(str) {
      return (str || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    // [FF-010] Highlight query term in text snippet
    function highlight(text, q) {
      if (!text || !q) return '';
      const safe = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      return text.replace(new RegExp(`(${safe})`, 'gi'), '<mark>$1</mark>');
    }

    input.addEventListener('focus', () => {
      if (!index) {
        fetch(root + 'search_index.json')
          .then(r => r.json())
          .then(data => { index = data; })
          .catch(err => console.warn('[Search] Index load failed', err));
      }
    });

    input.addEventListener('input', () => {
      const raw = input.value.trim();
      const q = normalize(raw);

      if (q.length < 2 || !index) {
        resultsContainer.hidden = true;
        resultsContainer.innerHTML = '';
        return;
      }

      // [FF-010] Busca em title_en, title_pt, content, slug — todos normalizados
      const matches = index.filter(item => {
        return normalize(item.title_en).includes(q)
            || normalize(item.title_pt).includes(q)
            || normalize(item.content).includes(q)
            || normalize(item.slug).includes(q);
      }).slice(0, 20);

      if (matches.length === 0) {
        resultsContainer.innerHTML = '<p>No results.</p>';
        resultsContainer.hidden = false;
        return;
      }

      const ul = document.createElement('ul');
      matches.forEach(item => {
        const li = document.createElement('li');

        // Título com highlight
        const a = document.createElement('a');
        a.href = root + item.url;                          // FF-010: era item.slug + '/index.html'
        a.innerHTML = highlight(item.title_en || item.pdpn, raw); // FF-010: era item.title

        // Snippet de conteúdo com highlight
        if (item.content) {
          const nContent = normalize(item.content);
          const pos = nContent.indexOf(q);
          if (pos !== -1) {
            const start = Math.max(0, pos - 60);
            const end = Math.min(item.content.length, pos + q.length + 60);
            const snippet = (start > 0 ? '…' : '') + item.content.slice(start, end) + (end < item.content.length ? '…' : '');
            const small = document.createElement('small');
            small.innerHTML = highlight(snippet, raw);
            li.appendChild(a);
            li.appendChild(small);
          } else {
            li.appendChild(a);
          }
        } else {
          li.appendChild(a);
        }

        ul.appendChild(li);
      });

      resultsContainer.innerHTML = '';
      resultsContainer.appendChild(ul);
      resultsContainer.hidden = false;
    });
  }

  function initViewMode() {
    // Restore last chosen view mode from localStorage
    try {
      const saved = localStorage.getItem('axis-view-mode');
      if (saved === 'comparative') setViewMode('comparative');
    } catch(e) {}
  }

  function cleanupLegacyServiceWorker() {
    // SW is intentionally disabled in base.html. If an older deployment
    // left registrations/caches behind, they can cause stale loading loops.
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations()
        .then(function(registrations) {
          registrations.forEach(function(reg) {
            reg.unregister().catch(function() {});
          });
        })
        .catch(function() {});
    }

    if ('caches' in window) {
      caches.keys()
        .then(function(keys) {
          keys
            .filter(function(k) { return k.indexOf('axis-niddhi-') === 0; })
            .forEach(function(k) { caches.delete(k).catch(function() {}); });
        })
        .catch(function() {});
    }
  }


  // ── FF-014 READING ENGINE ──────────────────────────────────────────────────

  // 1. Reading Progress Bar
  function updateReadingProgress() {
    const bar = document.getElementById('reading-progress');
    if (!bar) return;
    const scrollTop  = window.scrollY;
    const docHeight  = document.documentElement.scrollHeight - window.innerHeight;
    const pct        = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    bar.style.width  = Math.min(pct, 100) + '%';
  }

  // 2. Scroll Position Memory — per-page key
  function saveScrollPosition() {
    try { localStorage.setItem('scroll_' + location.pathname, window.scrollY); }
    catch(e) {}
  }

  function restoreScrollPosition() {
    try {
      const pos = localStorage.getItem('scroll_' + location.pathname);
      if (pos && parseInt(pos) > 0) {
        setTimeout(() => window.scrollTo({ top: parseInt(pos), behavior: 'instant' }), 50);
      }
    } catch(e) {}
  }

  // 3. Active Section Highlight via IntersectionObserver
  // Template uses .library-section (not .section-container per Aloka's spec)
  function initSectionHighlight() {
    const sections = document.querySelectorAll('.library-section');
    if (!sections.length || !('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          sections.forEach(s => s.classList.remove('active'));
          entry.target.classList.add('active');
        }
      });
    }, { rootMargin: '-40% 0px -40% 0px', threshold: 0 });

    sections.forEach(sec => observer.observe(sec));
  }

  // ── END FF-014 ────────────────────────────────────────────────────────────

  // --- SPRINT G: Section Boxes Colasáveis (h5 → wrapper) ---
  function initSectionBoxes() {
    // Extrair PDPN do URL: /pages/BD.AA.000/index.html → "BD.AA.000"
    const pdpnMatch = window.location.pathname.match(/\/pages\/([^/]+)/);
    const pdpn = pdpnMatch ? pdpnMatch[1] : 'index';
    const storageKey = 'sections-' + pdpn;

    // Recuperar estados salvos
    let savedState = {};
    try { savedState = JSON.parse(sessionStorage.getItem(storageKey) || '{}'); } catch(e) {}

    // Slug simples a partir do texto do h5
    function toSlug(text) {
      return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
    }

    // Salvar estado atual
    function saveState(slug, isCollapsed) {
      savedState[slug] = isCollapsed;
      try { sessionStorage.setItem(storageKey, JSON.stringify(savedState)); } catch(e) {}
    }

    // Processar cada container de conteúdo
    ['content-en', 'content-pt'].forEach(function(containerId) {
      const container = document.getElementById(containerId);
      if (!container) return;

      const h5s = Array.from(container.querySelectorAll('h5'));
      if (!h5s.length) return;

      h5s.forEach(function(h5) {
        const slug = toSlug(h5.textContent || '');

        // Coletar siblings até o próximo h5 ou fim do container
        const siblings = [];
        let next = h5.nextSibling;
        while (next && !(next.nodeName === 'H5')) {
          siblings.push(next);
          next = next.nextSibling;
        }

        // Criar wrapper .section-content
        const wrapper = document.createElement('div');
        wrapper.className = 'section-content';
        wrapper.setAttribute('data-h5-slug', slug);

        // Inserir wrapper após o h5 e mover siblings para dentro
        h5.parentNode.insertBefore(wrapper, h5.nextSibling);
        siblings.forEach(function(el) { wrapper.appendChild(el); });

        // Restaurar estado salvo (padrão: expandido)
        if (savedState[slug] === true) {
          h5.classList.add('collapsed');
          wrapper.classList.add('collapsed');
        }

        // Evento de click
        h5.addEventListener('click', function() {
          const isCollapsed = h5.classList.toggle('collapsed');
          wrapper.classList.toggle('collapsed', isCollapsed);
          saveState(slug, isCollapsed);
        });
      });
    });
  }

  // --- SPRINT 7: Print Markers ---
  function initPrintVideoMarkers() {
      document.querySelectorAll('iframe[src*="youtube"], iframe[src*="youtu.be"]').forEach(iframe => {
          if (iframe.previousElementSibling && iframe.previousElementSibling.classList.contains('print-video-marker')) {
              return;
          }

          const marker = document.createElement('div');
          marker.className = 'print-video-marker';

          const header = document.createElement('strong');
          header.textContent = 'Video omitted in print / Vídeo omitido na impressão';
          marker.appendChild(header);
          marker.appendChild(document.createElement('br'));

          const source = document.createElement('strong');
          source.textContent = 'Source/Fonte: ';
          marker.appendChild(source);
          marker.appendChild(document.createTextNode('YouTube'));
          marker.appendChild(document.createElement('br'));

          const title = document.createElement('strong');
          title.textContent = 'Title/Título: ';
          marker.appendChild(title);
          marker.appendChild(document.createTextNode(iframe.title || 'Embedded YouTube video'));
          marker.appendChild(document.createElement('br'));

          const url = document.createElement('strong');
          url.textContent = 'URL: ';
          marker.appendChild(url);
          marker.appendChild(document.createTextNode(iframe.src));

          const printHiddenContainer = iframe.closest('.video-container, .youtube-wrapper') || iframe;
          printHiddenContainer.parentNode.insertBefore(marker, printHiddenContainer);
      });
  }


  // --- Print Review Banner ---
  function initPrintReviewBanner() {
      if (document.querySelector('.print-review-banner')) {
          return;
      }

      const article = document.querySelector('article.content-block');
      if (!article) {
          return;
      }

      const pdpn = article.getAttribute('data-pdpn') || 'unknown';

      const banner = document.createElement('div');
      banner.className = 'print-review-banner';

      const header = document.createElement('strong');
      header.textContent = 'DRAFT / RASCUNHO';
      banner.appendChild(header);
      banner.appendChild(document.createElement('br'));

      banner.appendChild(document.createTextNode('Translation review copy / Cópia para revisão de tradução'));
      banner.appendChild(document.createElement('br'));

      banner.appendChild(document.createTextNode('Source/Fonte: PureDhamma.net'));
      banner.appendChild(document.createElement('br'));

      banner.appendChild(document.createTextNode('AXIS-NIDDHI page URL / URL da página AXIS-NIDDHI: '));
      const urlSpan = document.createElement('span');
      urlSpan.className = 'print-review-url';
      urlSpan.textContent = window.location.href;
      banner.appendChild(urlSpan);
      banner.appendChild(document.createElement('br'));

      banner.appendChild(document.createTextNode('Canonical ID / ID canônico: ' + pdpn));
      banner.appendChild(document.createElement('br'));

      banner.appendChild(document.createTextNode('Note/Nota: This printed/PDF copy is for review and archival traceability. The doctrinal source remains PureDhamma.net.'));
      banner.appendChild(document.createElement('br'));
      banner.appendChild(document.createElement('br'));

      const legendHeader = document.createElement('strong');
      legendHeader.textContent = 'COLOR LEGEND / LEGENDA DE CORES:';
      banner.appendChild(legendHeader);
      banner.appendChild(document.createElement('br'));

      const legendGlossarySpan = document.createElement('span');
      legendGlossarySpan.className = 'print-legend-glossary';
      legendGlossarySpan.textContent = 'Orange/Laranja';
      banner.appendChild(legendGlossarySpan);
      banner.appendChild(document.createTextNode(' = Glossary term / Termo protegido do glossário'));
      banner.appendChild(document.createElement('br'));

      const legendAudioSpan = document.createElement('span');
      legendAudioSpan.className = 'print-legend-audio';
      legendAudioSpan.textContent = 'Red/Vermelho';
      banner.appendChild(legendAudioSpan);
      banner.appendChild(document.createTextNode(' = Glossary term with audio / Termo do glossário com áudio'));

      article.parentNode.insertBefore(banner, article);
  }

  document.addEventListener('DOMContentLoaded', () => {
    cleanupLegacyServiceWorker();
    initTheme();
    initViewMode();       // [FF-012]
    restoreScrollPosition(); // [FF-014]
    initSectionHighlight();  // [FF-014]
    initLang();
    initAccordion();
    initSectionListToggle();
    initInlineSectionReveal();
    initArticleLinkTargets();
    initSectionBoxes();   // [SPRINT G] h5 colasáveis
    initPronunciation();
    initSearch(); // [Sprint 9]
    initPrintVideoMarkers(); // [Sprint 7 Print Setup]
    initPrintReviewBanner(); // Print review traceability banner
    generateTOC('content-en', 'toc-list-en');
    if (document.getElementById('content-pt')) {
      generateTOC('content-pt', 'toc-list-pt');
    }

    // [SPRINT L] BUG 1: meta-toggle via event listener (onclick inline estava quebrado)
    const metaBtn = document.getElementById('meta-toggle-btn');
    if (metaBtn) {
      metaBtn.addEventListener('click', () => {
        const wrap = metaBtn.closest('.meta-toggle-wrap');
        const isOpen = wrap.classList.toggle('open');
        metaBtn.setAttribute('aria-expanded', String(isOpen));
      });
    }
  });

  // FF-014: scroll listeners (passive for performance)
  window.addEventListener('scroll', updateReadingProgress, { passive: true });
  window.addEventListener('scroll', saveScrollPosition,    { passive: true });

})();

// --- PRINT & PRESERVATION MODAL LOGIC ---
function openPrintModal() {
    document.getElementById('print-modal').classList.add('active');
    document.getElementById('print-modal-overlay').classList.add('active');
}

function closePrintModal() {
    document.getElementById('print-modal').classList.remove('active');
    document.getElementById('print-modal-overlay').classList.remove('active');
}

function executePrint() {
    const marginType = document.getElementById('p-margin').value;
    const lineHeight = document.getElementById('p-line').value;
    const colorSelect = document.getElementById('p-color');
    const colorMode = colorSelect ? colorSelect.value : 'bw';
    const root = document.documentElement;

    root.style.setProperty('--print-line-height', lineHeight);

    if (marginType === 'compact') {
        root.style.setProperty('--print-pad', '0');
    } else if (marginType === 'wide') {
        root.style.setProperty('--print-pad', '0 5cm 0 0'); // Wide right margin for ink notes
    } else {
        root.style.setProperty('--print-pad', '0 1cm'); // Normal minimal breathing room
    }

    if (colorMode === 'color') {
        root.style.setProperty('--print-text-color', 'inherit');
        root.style.setProperty('--print-heading-color', 'var(--green-axiom, #008800)');
        root.style.setProperty('--print-link-color', 'var(--link-color, #2b5fac)');
        root.style.setProperty('--print-color-adjust', 'exact');
        root.classList.add('print-colors');
    } else {
        root.style.setProperty('--print-text-color', 'black');
        root.style.setProperty('--print-heading-color', 'black');
        root.style.setProperty('--print-link-color', 'black');
        root.style.setProperty('--print-color-adjust', 'economy');
        root.classList.remove('print-colors');
    }

    closePrintModal();
    // Allow DOM to apply variables briefly before triggering the print spooler
    setTimeout(() => { window.print(); }, 100);
}

// --- TOC TOGGLE (SPRINT C) ---
window.toggleTOC = function(targetId) {
    const el = document.getElementById(targetId);
    if(el) {
        if (el.style.display === 'none' || el.style.display === '') {
            el.style.display = 'block';
        } else {
            el.style.display = 'none';
        }
    }
};
