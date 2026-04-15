/**
 * BRASILEIRINHO ENGINE — UNIFIED FRONTEND LOGIC V1.3.0
 * [20260222] Added: initPronunciation() — click-to-play Pāli audio affordance
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


  // [20260222] SPRINT 9 — Phase 2: Pronunciation Affordance
  //
  // Strategy:
  //   1. Fetch pronunciation_manifest.json from site root (path calculated
  //      dynamically from current page depth — works in root AND subfolders).
  //   2. Find all .term-highlight elements in the page.
  //   3. For terms with available audio: add .has-audio + onclick play.
  //   4. Click-to-play only — no hover autoplay (respects "zen silence" axiom).
  //   5. Degrades gracefully: if JS disabled or manifest missing, tooltip still works.
  //
  // Path strategy (root-relative, depth-aware):
  //   Root page  (depth 0): ./pronunciation_manifest.json
  //   Post page  (depth 1): ../pronunciation_manifest.json
  //   Calculated via pathname split — no hardcoded absolute paths.

  function getRootPath() {                                   // [20260222]
    // Returns the relative path prefix to reach site root from current page.
    // Examples:
    //   /index.html         → './'
    //   /TL.BB.003/index.html → '../'
    var parts = window.location.pathname.replace(/\/+$/, '').split('/');
    // parts[-1] is filename, parts[-2] is folder (if any)
    // depth = number of folders below root
    var depth = parts.length - 2; // subtract '' (root) and filename
    if (depth <= 0) return './';
    return '../'.repeat(depth);
  }

  function initPronunciation() {                             // [20260222]
    var terms = document.querySelectorAll('.term-highlight');
    if (!terms.length) return;

    var root = getRootPath();
    var manifestUrl = root + 'pronunciation_manifest.json'; // [20260222]

    fetch(manifestUrl)
      .then(function(r) {
        if (!r.ok) throw new Error('Manifest not found: ' + manifestUrl);
        return r.json();
      })
      .then(function(manifest) {
        var audioBase = root + 'assets/audio/en-US/';       // [20260222]

        terms.forEach(function(el) {
          var termKey = el.getAttribute('data-term');
          if (!termKey) return;

          var entry = manifest.terms && manifest.terms[termKey];
          if (!entry || !entry.available || !entry.mp3) return;

          // Term has audio — add affordance
          el.classList.add('has-audio');                     // [20260222]

          el.addEventListener('click', function(e) {        // [20260222]
            e.preventDefault();
            var audioPath = audioBase + entry.mp3;
            var audio = new Audio(audioPath);
            audio.play().catch(function(err) {
              console.warn('[Pronunciation] Could not play:', audioPath, err);
            });
          });
        });
      })
      .catch(function(err) {
        // Graceful degradation — no audio affordance, tooltips still work
        console.warn('[Pronunciation] Could not load manifest:', err);
      });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initLang();
    initAccordion();
    initPronunciation();    // [20260222]
    generateTOC('content-en', 'toc-list-en');
    if (document.getElementById('content-pt')) {
      generateTOC('content-pt', 'toc-list-pt');
    }
  });

})();
