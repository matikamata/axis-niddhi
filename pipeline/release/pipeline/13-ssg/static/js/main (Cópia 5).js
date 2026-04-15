/* pipeline/13-ssg/static/js/main.js */

/**
 * BRASILEIRINHO ENGINE — UNIFIED FRONTEND LOGIC V1.4.2
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
    document.querySelectorAll('.library-section').forEach(section => {
      const h2 = section.querySelector('h2');
      if (!h2) return;

      h2.addEventListener('click', () => {
        h2.classList.toggle('active');
      });
    });
  }

  function getRootPath() {
    var parts = window.location.pathname.replace(/\/+$/, '').split('/');
    var depth = parts.length - 2;
    if (depth <= 0) return './';
    return '../'.repeat(depth);
  }

  function initPronunciation() {
    var terms = document.querySelectorAll('.term-highlight');
    if (!terms.length) {
      console.log('[Pronunciation] No .term-highlight elements found on this page.');
      return;
    }

    var root = getRootPath();
    var manifestUrl = root + 'pronunciation_manifest.json';
    console.log('[Pronunciation] Loading manifest from:', manifestUrl, '| terms found:', terms.length);

    fetch(manifestUrl)
      .then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status + ' — ' + manifestUrl);
        return r.json();
      })
      .then(function(manifest) {

        // [PATCH-B2 2026-03-09] Dual-schema loader with NFC normalization:
        //   1. Structured schema: manifest.terms[key] → { available, mp3, ... }
        //   2. Flat fallback:     manifest[key]        → "assets/audio/en-US/file.mp3"
        //   NFC normalization fixes diacritic mismatch between HTML data-term
        //   (written by Python/BS4, may be NFD) and JSON keys (NFC in manifest).
        function resolveAudioPath(termKey) {
          // Normalize to NFC for consistent Unicode comparison
          var key = termKey.normalize ? termKey.normalize('NFC') : termKey;

          if (manifest.terms) {
            // Structured schema
            var entry = manifest.terms[key] || manifest.terms[termKey];
            if (entry && entry.available && entry.mp3) {
              return root + 'assets/audio/en-US/' + entry.mp3;
            }
            return null;
          }
          // Flat fallback: values are root-relative paths
          var flat = manifest[key] || manifest[termKey];
          if (!flat) return null;
          return root + flat;
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
            var audio = new Audio(audioPath);
            audio.play().catch(function(err) {
              console.warn('[Pronunciation] Could not play:', audioPath, err);
            });
          });
        });

        console.log('[Pronunciation] Ready. Terms with audio:', activated, '/', terms.length);
      })
      .catch(function(err) {
        console.warn('[Pronunciation] Could not load manifest:', err);
      });
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

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initViewMode(); // [FF-012]
    initLang();
    initAccordion();
    initPronunciation();
    initSearch(); // [Sprint 9]
    generateTOC('content-en', 'toc-list-en');
    if (document.getElementById('content-pt')) {
      generateTOC('content-pt', 'toc-list-pt');
    }
  });

})();
