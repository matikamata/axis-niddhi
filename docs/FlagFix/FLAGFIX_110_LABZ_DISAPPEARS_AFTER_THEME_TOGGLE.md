# #FlagFix_110 — LABZ Disappears After Theme Toggle

Date: 2026-05-19  
Workspace: `/home/sanghop/axis/axis-niddhi-production`

## Observed bug
In local published review (`http://localhost:8088/archive.html`), LABZ flowers rendered initially, but disappeared after theme button interaction, and did not reliably return without refresh.

## Root cause
Runtime state conflict between normal theme controls and LABZ state:

1. Theme buttons always wrote `data-theme` directly (light/dark/sunrise/colirio/sunset), which immediately exits `stardust` and hides LABZ ambient layer.
2. LABZ used `axis-niddhi-theme` and `axis-theme-pre-labz` keys, while normal theme init used `br_theme`, creating state drift across toggles/reloads.
3. LABZ state restore depended on mismatched storage assumptions, so behavior after theme interactions was inconsistent.

## Files inspected
- `pipeline/13-static-site/js/main.js`
- `pipeline/13-static-site/css/style.css`
- `pipeline/13-static-site/archive.html`
- `pipeline/13-ssg/static/js/main.js`
- `pipeline/13-ssg/static/css/style.css`
- `pipeline/13-ssg/templates/base.html`

## Patch applied
Yes, minimal patch applied to JS source + static pair:
- `pipeline/13-ssg/static/js/main.js`
- `pipeline/13-static-site/js/main.js`

No CSS/template/asset edits were needed.

## Behavior change (before/after)
Before:
- Clicking theme button during LABZ could drop `stardust` rendering state and de-sync stored state.

After:
- If LABZ is active (`data-theme="stardust"`), clicking a theme button updates only the LABZ exit theme (`axis-theme-pre-labz`) and `br_theme`, without disabling LABZ immediately.
- `initTheme()` now restores LABZ explicitly from `axis-niddhi-theme === "stardust"`.
- Exiting LABZ synchronizes `br_theme` with restored non-LABZ theme.

## Local validation steps
1. Open `archive.html`.
2. Activate LABZ.
3. Click theme buttons while LABZ is active:
   - LABZ visuals should remain active (stardust preserved).
4. Exit LABZ:
   - selected exit theme should apply cleanly.
5. Reload page:
   - LABZ/non-LABZ state should be consistent with stored values.

## Published payload touched?
No. `axis-niddhi-published` was not modified in this sprint.

## Recommendation for #111
`#FlagFix_111 — Published payload sync for LABZ theme-toggle runtime fix + local smoke check`
