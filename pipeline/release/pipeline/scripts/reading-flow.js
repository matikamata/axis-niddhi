/* static/js/reading-flow.js */
(function() {
    'use strict';

    // --- CONFIG ---
    const MEMORY_KEY = 'brasileirinho_reading_state';
    const GREEN_AXIOM = '#00ff00';

    // --- 1. THE GREEN THREAD (Progress Bar) ---
    function initProgressBar() {
        const hook = document.getElementById('reading-progress-hook');
        if (!hook) return;

        // Inject styles dynamically to avoid touching style.css
        hook.style.position = 'fixed';
        hook.style.top = '0';
        hook.style.left = '0';
        hook.style.height = '3px';
        hook.style.backgroundColor = GREEN_AXIOM;
        hook.style.width = '0%';
        hook.style.zIndex = '10000';
        hook.style.transition = 'width 0.1s ease-out';
        hook.style.display = 'block'; // Activate the hook

        window.addEventListener('scroll', () => {
            const scrollTop = window.scrollY;
            const docHeight = document.body.scrollHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            hook.style.width = scrollPercent + '%';
            
            // Save scroll position periodically (debounce)
            if (Math.abs(scrollPercent - lastSavedPercent) > 5) {
                saveState();
                lastSavedPercent = scrollPercent;
            }
        }, { passive: true });
    }
    let lastSavedPercent = 0;

    // --- 2. THE MEMORY (Save State) ---
    function saveState() {
        const article = document.querySelector('article.content-en'); // Source of truth
        if (!article) return;

        const state = {
            pdpn: article.dataset.pdpn,
            title: document.title.split('|')[0].trim(),
            url: window.location.href,
            scrollY: window.scrollY,
            timestamp: Date.now()
        };
        localStorage.setItem(MEMORY_KEY, JSON.stringify(state));
    }

    // --- 3. THE COMPASS (Density Indicator) ---
    function initCompass() {
        const article = document.querySelector('article.content-en');
        const metaContainer = document.querySelector('.meta');
        
        if (!article || !metaContainer) return;

        const time = article.dataset.readingTime;
        const level = article.dataset.level;

        if (time && level) {
            const span = document.createElement('span');
            span.style.marginLeft = '1rem';
            span.style.paddingLeft = '1rem';
            span.style.borderLeft = '1px solid #ccc';
            span.style.fontSize = '0.85rem';
            span.style.color = 'var(--meta-color)';
            
            // Icons for density
            let icon = '🌱'; // Intro
            if (level === 'intermediate') icon = '🌿';
            if (level === 'advanced') icon = '🌳';

            span.innerHTML = `${icon} ${time} min`;
            span.title = `Density: ${level}`;
            
            metaContainer.appendChild(span);
        }
    }

    // --- 4. THE RETURN (Resume on Index) ---
    function initResume() {
        // Only run on index page (check for threshold header)
        if (!document.querySelector('.threshold-header')) return;

        try {
            const raw = localStorage.getItem(MEMORY_KEY);
            if (!raw) return;
            const state = JSON.parse(raw);

            // Expiry: 7 days
            if (Date.now() - state.timestamp > 7 * 24 * 60 * 60 * 1000) return;

            const container = document.querySelector('.mission-statement');
            if (container) {
                const resumeLink = document.createElement('div');
                resumeLink.style.marginTop = '1.5rem';
                resumeLink.style.fontSize = '0.9rem';
                resumeLink.innerHTML = `
                    <span style="opacity: 0.6">Continue reading:</span> 
                    <a href="${state.url}" style="color: var(--green-axiom); font-weight: bold;">
                        ${state.title} ↪
                    </a>
                `;
                container.parentNode.insertBefore(resumeLink, container.nextSibling);
            }
        } catch (e) { console.error(e); }
    }

    // --- INIT ---
    document.addEventListener('DOMContentLoaded', () => {
        initProgressBar();
        initCompass();
        initResume();
        
        // Restore scroll if returning to same page
        const article = document.querySelector('article.content-en');
        if (article) {
            const raw = localStorage.getItem(MEMORY_KEY);
            if (raw) {
                const state = JSON.parse(raw);
                if (state.pdpn === article.dataset.pdpn && state.scrollY > 0) {
                    // Optional: Add a "Jump to where you left off" toast here
                    // For V1, we just silently update state, we don't auto-scroll to avoid disorientation
                }
            }
        }
    });

})();
