// pipeline/13-ssg/static/js/sw.js
// Service Worker — Brasileirinho Engine v2.0.0
// Strategy: Progressive (shell-first) + Agency Layer (user-initiated full cache)
// [20260222] Integrado ao pipeline por Vayo (Claude Sonnet 4.6)
//
// ARQUITETURA:
//   FULL_PRECACHE = false  → padrão — só shell (~5 arquivos) é pré-cacheado
//   FULL_PRECACHE = true   → NÃO usar automaticamente — 160MB+ de download
//
// AGENCY LAYER:
//   A função cachePostsForOffline() pode ser chamada pelo UI (botão "Save for Offline")
//   quando o USUÁRIO decidir baixar o conteúdo completo.
//   Nunca é acionada automaticamente.
//
// ESTRATÉGIA DE FETCH:
//   - Shell (CSS, index.json, nav): cache-first
//   - Posts HTML: network-first, cache fallback
//   - Assets (imagens, MP3): cache-on-demand

'use strict';

// [20260222] CACHE_NAME versionado — ao mudar, o activate limpa o cache anterior.
// Tied to build version — update when template_hash changes in build.py.
const CACHE_VERSION = 'v2.0.0';                                    // [20260222]
const CACHE_NAME    = `brasileirinho-${CACHE_VERSION}`;            // [20260222]

// [20260222] Shell: arquivos mínimos para o app funcionar offline.
// Todos os caminhos são relativos à raiz do site.
const SHELL_URLS = [                                               // [20260222]
    './',                              // Landing page (index.html)
    './css/style.css',                 // CSS tokens — gerado por build.py
    './js/main.js',                    // Progressive enhancement
    './js/reading-flow.js',            // Reading flow JS
    './index.json',                    // Nav tree — gerado por _generate_nav_index()
    './pronunciation_manifest.json',   // Áudio manifest — gerado por _generate_pronunciation_manifest()
    // './favicon.ico',               // Adicionar quando existir
];

// [20260222] Toggle de precache total — NÃO mudar para true automaticamente.
// Só para uso consciente em builds locais ou distribuição offline deliberada.
const FULL_PRECACHE = false;                                       // [20260222]


// ─── INSTALL ────────────────────────────────────────────────────────────────
// Pré-cacheia apenas o shell. Rápido, não força download de conteúdo.

self.addEventListener('install', event => {                        // [20260222]
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log(`[SW] Installing shell cache: ${CACHE_NAME}`);
                return cache.addAll(SHELL_URLS);
            })
            .then(() => self.skipWaiting())
    );
});


// ─── ACTIVATE ───────────────────────────────────────────────────────────────
// Limpa caches antigos quando o CACHE_VERSION mudar.

self.addEventListener('activate', event => {                       // [20260222]
    event.waitUntil(
        caches.keys()
            .then(cacheNames => Promise.all(
                cacheNames
                    .filter(name => name.startsWith('brasileirinho-') && name !== CACHE_NAME)
                    .map(name => {
                        console.log(`[SW] Removing old cache: ${name}`);
                        return caches.delete(name);
                    })
            ))
            .then(() => self.clients.claim())
    );
});


// ─── FETCH ──────────────────────────────────────────────────────────────────
// Estratégia mista:
//   - Shell (CSS, JS, index.json): cache-first (estáveis entre builds)
//   - Posts HTML: network-first, fallback para cache
//   - Assets (imagens, MP3): cache-on-demand

self.addEventListener('fetch', event => {                          // [20260222]
    const url = new URL(event.request.url);

    // Ignorar requests não-GET e cross-origin
    if (event.request.method !== 'GET') return;
    if (url.origin !== self.location.origin) return;

    const path = url.pathname;

    // Cache-first: shell estático
    const isShell = (
        path.endsWith('.css') ||
        path.endsWith('main.js') ||
        path.endsWith('reading-flow.js') ||
        path.endsWith('index.json') ||
        path.endsWith('pronunciation_manifest.json') ||
        path.endsWith('sw_mp3_manifest.json')
    );

    if (isShell) {
        event.respondWith(cacheFirst(event.request));
        return;
    }

    // Cache-on-demand: MP3 (grandes, não pré-cacheados)
    if (path.endsWith('.mp3')) {
        event.respondWith(cacheOnDemand(event.request));
        return;
    }

    // Network-first: posts HTML e tudo mais
    event.respondWith(networkFirst(event.request));
});


// ─── ESTRATÉGIAS ────────────────────────────────────────────────────────────

function cacheFirst(request) {                                     // [20260222]
    return caches.match(request).then(cached => {
        if (cached) return cached;
        return fetchAndCache(request);
    });
}

function networkFirst(request) {                                   // [20260222]
    return fetch(request)
        .then(response => {
            if (response.ok) cacheResponse(request, response.clone());
            return response;
        })
        .catch(() => caches.match(request));  // fallback para cache se offline
}

function cacheOnDemand(request) {                                  // [20260222]
    // Não pré-cacheia — só armazena após primeira requisição do usuário
    return caches.match(request).then(cached => {
        if (cached) return cached;
        return fetchAndCache(request);
    });
}

function fetchAndCache(request) {
    return fetch(request).then(response => {
        if (response.ok) cacheResponse(request, response.clone());
        return response;
    });
}

function cacheResponse(request, response) {
    caches.open(CACHE_NAME).then(cache => cache.put(request, response));
}


// ─── AGENCY LAYER ───────────────────────────────────────────────────────────
// [20260222] Download offline iniciado APENAS pelo usuário (via postMessage do UI).
// Nunca chamado automaticamente pelo SW.
// O UI envia: { type: 'CACHE_POSTS', urls: [...] }

self.addEventListener('message', event => {                        // [20260222]
    if (event.data && event.data.type === 'CACHE_POSTS') {
        const urls = event.data.urls || [];
        cachePostsForOffline(urls).then(() => {
            event.source.postMessage({
                type: 'CACHE_POSTS_DONE',
                count: urls.length
            });
        });
    }
});

async function cachePostsForOffline(urls) {                        // [20260222]
    // [20260222] PLACEHOLDER: o UI deve enviar a lista de URLs a cachear.
    // Exemplo de como o UI constrói a lista a partir do index.json:
    //
    //   const index = await fetch('./index.json').then(r => r.json());
    //   const urls  = index.sections.flatMap(s =>
    //     s.posts.map(p => `./${p.pdpn}/index.html`)
    //   );
    //   navigator.serviceWorker.controller.postMessage({ type: 'CACHE_POSTS', urls });
    //
    const cache = await caches.open(CACHE_NAME);
    for (const url of urls) {
        try {
            const response = await fetch(url);
            if (response.ok) await cache.put(url, response);
        } catch (e) {
            console.warn(`[SW] Could not cache: ${url}`);
        }
    }
    console.log(`[SW] Agency Layer: ${urls.length} posts cached for offline.`);
}
