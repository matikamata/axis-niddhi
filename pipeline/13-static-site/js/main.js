/* pipeline/13-ssg/static/js/main.js */

/**
 * AXIS-NIDDHI ENGINE — UNIFIED FRONTEND LOGIC V1.5.0
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

  if (isActive) {
    // Restaurar tema anterior
    const prev = localStorage.getItem('axis-theme-pre-labz') || 'dark';
    document.body.setAttribute('data-theme', prev);
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
    { id: 'light', icon: '☀️' },
    { id: 'dark', icon: '🌙' },
    { id: 'colirio', icon: '🌿' },
    { id: 'sunset', icon: '🌅' },
    { id: 'sunrise', icon: '🏔️' }
    // stardust é gerido pelo toggleLabz() — não aparece no theme switcher normal
  ];

  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) document.body.setAttribute('data-theme', saved);
    // [FF-013] Restore labz button state if stardust was active
    if (saved === 'stardust') {
      const btn = document.getElementById('labz-btn');
      const banner = document.getElementById('labz-banner');
      btn    && btn.classList.add('labz-active');
      banner && banner.classList.add('visible');
    }

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
    const sections = document.querySelectorAll('.library-section');
    sections.forEach(section => {
      const h2 = section.querySelector('h2');
      if (!h2) return;

      h2.addEventListener('click', () => {
        h2.classList.toggle('active');
      });
    });

    // SPRINT 14: Auto-expand section if hash matches
    function handleHash() {
      const hash = window.location.hash;
      if (!hash) return;
      const target = document.querySelector(hash);
      if (target && target.classList.contains('library-section')) {
        const h2 = target.querySelector('h2');
        if (h2) h2.classList.add('active');
        // Smooth scroll to ensure visibility
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    window.addEventListener('hashchange', handleHash);
    handleHash(); // Run on load
  }

  function getRootPath() {
    var path = window.location.pathname;
    // Remove leading/trailing slashes and split
    var parts = path.split('/').filter(p => p !== '');
    
    // Depth Counting for Netlify Pretty URLs:
    // 1. /archive -> parts: ['archive']. depth: 0
    // 2. /pages/TL.CC.003/ -> parts: ['pages', 'TL.CC.003']. depth: 2
    // 3. /pages/TL.CC.003/index.html -> parts: ['pages', 'TL.CC.003', 'index.html']. depth: 2
    
    var depth = 0;
    if (parts.length > 0) {
      // If the last part has an extension, it's a file, so it doesn't add to depth
      var lastPart = parts[parts.length - 1];
      var isFile = lastPart.indexOf('.') !== -1 && !/^[A-Z]{2}\.[A-Z]{2}\.\d{3}$/.test(lastPart);
      // Wait, our PDPNs like TL.CC.003 have dots. 
      // Most reliable check for Netlify: the 'pages' directory is always level 1.
      if (parts[0] === 'pages') {
        depth = 2; // Always 2 levels deep for posts in the current architecture
      } else {
        depth = 0; // Root level for archive, index, etc.
      }
    }

    if (depth <= 0) return './';
    return '../'.repeat(depth);
  }

  function initPronunciation() {
    var terms = document.querySelectorAll('.term-highlight');
    if (!terms.length) return;

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
            // FALLBACK: Try absolute root as suggested by Gemini
            loadManifest('/pronunciation_manifest.json', true);
          }
        });
    }

    function setupAudio(manifest, currentRoot) {
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
        // If path starts with / it's already absolute (Gemini suggestion)
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
          var audio = new Audio(audioPath);
          audio.play().catch(function(err) {
            console.warn('[Pronunciation] Play failed:', audioPath, err);
            // FINAL FALLBACK: Try absolute path if relative failed
            if (!audioPath.startsWith('/')) {
              var absPath = '/' + audioPath.replace(/^\.+\//, '');
              console.log('[Pronunciation] Retrying absolute:', absPath);
              new Audio(absPath).play().catch(e => {});
            }
          });
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

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initViewMode();       // [FF-012]
    restoreScrollPosition(); // [FF-014]
    initSectionHighlight();  // [FF-014]
    initLang();
    initAccordion();
    initPronunciation();
    initSearch(); // [Sprint 9]
    generateTOC('content-en', 'toc-list-en');
    if (document.getElementById('content-pt')) {
      generateTOC('content-pt', 'toc-list-pt');
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
    const root = document.documentElement;

    root.style.setProperty('--print-line-height', lineHeight);

    if (marginType === 'compact') {
        root.style.setProperty('--print-pad', '0');
    } else if (marginType === 'wide') {
        root.style.setProperty('--print-pad', '0 5cm 0 0'); // Wide right margin for ink notes
    } else {
        root.style.setProperty('--print-pad', '0 1cm'); // Normal minimal breathing room
    }

    closePrintModal();
    // Allow DOM to apply variables briefly before triggering the print spooler
    setTimeout(() => { window.print(); }, 100);
}

