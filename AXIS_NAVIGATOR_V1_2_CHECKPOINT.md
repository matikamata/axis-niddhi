# AXIS-NAVIGATOR v1.2 Checkpoint

## Current Branch

- `feat-axis-navigator-v1-1`

## Files Changed Since v1

- `pipeline/13-ssg/build.py`
- `pipeline/13-ssg/templates/base.html`
- `pipeline/13-ssg/templates/welcome.html`
- `pipeline/13-ssg/static/js/navigator-store.js`
- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/css/navigator.css`

## Implemented Features: v1 -> v1.2

### v1 MVP

- Floating Navigator button
- Right-side panel shell
- Cockpit modes: `asfalto`, `hover`, `javana`
- Local-first persistence with `localStorage`
- Quick Find using generated static JSON
- This Page metadata/status actions
- Resume Reading
- Recent History
- Study Paths
- Simple bookmarks/status tracking

### v1.1

- Quick Find improvements
  - stronger ranking
  - debounce
  - keyboard navigation
  - auto-focus
  - highlighted matches
- Page Outline from headings
- Related Pages via lightweight heuristic
- Micro visual refinement for This Page
  - spacing
  - density
  - hierarchy
  - hover/focus polish

### v1.2

- Javana Mode foundation
  - wider advanced panel
  - stronger visual distinction from Hover mode
  - Javana Workspace section inside This Page
- Javana placeholders
  - Concept Map
  - Split Reference
  - Deep Recall
- Lightweight Javana actions
  - open related page in new tab
  - copy current page URL
  - disabled pin placeholder
- Reuse of existing local study state inside Javana
  - recent visits count
  - current status
  - current study path membership

## Intentionally Unimplemented

- No backend
- No auth
- No cloud sync
- No embeddings
- No semantic engine
- No graph library
- No canvas graph
- No real split-screen engine
- No annotation engine
- No advanced recall algorithm
- No CSL changes
- No canonical content changes
- No deployment changes
- No build/deploy model changes beyond the original minimal v1 asset integration

## Safety Guarantees

- Progressive enhancement only
- Site remains readable without Navigator
- If Navigator JS fails, core reading page still works
- No backend dependency
- No external API dependency for reading UX
- No SPA conversion
- No canonical/CSL mutation
- No deployment config changes
- Work isolated to feature branch, not `main`
- Rollback is file-based and trivial

## localStorage Keys Used

- `axis.navigator.v1.preferences`
- `axis.navigator.v1.progress`
- `axis.navigator.v1.history`
- `axis.navigator.v1.paths`
- `axis.navigator.v1.bookmarks`

### Stored Preference Fields

- `cockpit_mode`
- `auto_resume`

### Stored Progress Fields

- `status`
- `percent`
- `lastScrollY`
- `lastVisitedAt`

## Test Checklist

### Base validation

- [ ] `node --check pipeline/13-ssg/static/js/navigator.js`
- [ ] `node --check pipeline/13-ssg/static/js/navigator-store.js`

### Core page checks

- [ ] Open `TL.JJ.008`
- [ ] Open one short page
- [ ] Open one page from another section

### Mode checks

- [ ] `Asfalto` remains minimal and quiet
- [ ] `Hover` remains practical and stable
- [ ] `Javana` opens wider panel correctly
- [ ] Javana Workspace appears only in `javana`

### Functional checks

- [ ] Quick Find still works
- [ ] Outline still works
- [ ] Related Pages still works
- [ ] Resume still works
- [ ] History still works
- [ ] Study Paths still works
- [ ] Bookmark/status still works
- [ ] Copy current page URL works in Javana
- [ ] Open related page in new tab works in Javana

### Layout checks

- [ ] No console errors
- [ ] No obvious layout break on desktop
- [ ] No bad overflow on narrow/mobile viewport

## Rollback Instructions

### Full Navigator rollback

Revert these files:

- `pipeline/13-ssg/build.py`
- `pipeline/13-ssg/templates/base.html`
- `pipeline/13-ssg/templates/welcome.html`
- `pipeline/13-ssg/static/js/navigator-store.js`
- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/css/navigator.css`

This removes all AXIS-NAVIGATOR integration and returns the site to pre-v1 behavior.

### Javana-only rollback

Revert only:

- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/css/navigator.css`

This removes v1.1/v1.2 Navigator behavior refinements, including Javana foundation, while preserving the original v1 integration points if desired.

## Status Summary

AXIS-NAVIGATOR v1.2 is currently a lightweight, local-first, non-canonical overlay with:

- stable v1 reading utilities
- v1.1 study/navigation improvements
- v1.2 Javana foundation for future advanced study mode

The system is still intentionally conservative:

- additive
- reversible
- static-site compatible
- production-safe by design
