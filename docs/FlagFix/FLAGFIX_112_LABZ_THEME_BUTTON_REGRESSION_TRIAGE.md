# #FlagFix_112 — LABZ Theme Button Regression Triage

Date: 2026-05-19  
Workspace: `/home/sanghop/axis/axis-niddhi-production`

## #111 human result
FAIL — after #110, theme buttons appeared non-functional during LABZ usage.

## Root cause
#110 introduced a guard that prevented theme buttons from updating `data-theme` while LABZ (`stardust`) was active.

Effect:
- user clicked theme buttons but page theme did not change;
- behavior looked like a dead theme switcher;
- state handling also mixed `br_theme` and `axis-niddhi-theme` in a way that caused inconsistent expectations.

## Diagnosis summary
- Theme handling code and LABZ handling code live in:
  - `pipeline/13-ssg/static/js/main.js`
  - `pipeline/13-static-site/js/main.js`
- Regression came from the `b.onclick` logic added in #110 that only updated `axis-theme-pre-labz` in LABZ mode, instead of switching theme.

## Patch applied?
Yes (minimal JS-only patch).

## Changed files
- `pipeline/13-ssg/static/js/main.js`
- `pipeline/13-static-site/js/main.js`
- `docs/FlagFix/FLAGFIX_112_LABZ_THEME_BUTTON_REGRESSION_TRIAGE.md`

## Patch behavior
1. Introduced small helper `setLabzUi(active)` for consistent LABZ button/banner UI state.
2. `initTheme()` now computes effective theme from:
   - `br_theme` (primary),
   - fallback `axis-niddhi-theme` (legacy),
   - fallback default `dark`.
3. Theme button click now always updates:
   - `data-theme`,
   - `br_theme`,
   - `axis-niddhi-theme`,
   and refreshes LABZ UI state accordingly.
4. When switching to non-stardust theme, stale `axis-theme-pre-labz` is cleared.

## Validation results
Commands run:
- `git diff --check`
- `git diff --stat`
- `git diff --name-status`

Result:
- clean diff checks;
- only expected JS files changed (plus this report).

## Published touched?
No. `axis-niddhi-published` was not modified in #112.

## No-change confirmations
- No deploy.
- No Netlify upload.
- No build/pipeline.
- No broad sync/copy.
- No CSL/metadata/TCC/SP10/SP11/DeepL/translation changes.
- No `.gitignore` changes.
- No LABZ image asset changes.

## Recommended #113
`#FlagFix_113 — Sync #112 JS runtime fix to published payload and run local human visual regression check`
