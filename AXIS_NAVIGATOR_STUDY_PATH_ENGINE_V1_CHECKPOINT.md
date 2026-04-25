# AXIS NAVIGATOR — Study Path Engine v1 Checkpoint

## Current branch

- `feat-axis-nana-gemini-vertex`
- no work was performed on `main`

## Files modified

Study Path Engine v1 source files:

- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/css/navigator.css`

Derived static-site refresh used for QA:

- `pipeline/13-static-site/js/navigator.js`
- `pipeline/13-static-site/css/navigator.css`
- `pipeline/13-static-site/pages/TL.JJ.008/index.html`

## localStorage keys used

- `axis.navigator.v1.preferences`
- `axis.navigator.v1.pinned_answers`
- `axis.navigator.v1.study_paths`

## UI sections added

Inside BeYond Mode + Study Mode ON:

- `Validated Answer`
  - `Pin to Study Path`
- `Study Desk`
  - `Create Study Path`
  - `Add to Path`
  - `Remove`
  - `Copy refs`
  - `Export Pins JSON`
- `Study Paths`
  - path cards with `Open` and `Delete`
  - path detail with:
    - `Add Current Page`
    - `Move ↑`
    - `Move ↓`
    - `Remove`
    - `Open source`
    - `Export Path JSON`

## Manual QA results

QA status:

- `partial / blocked by browser automation limitation`

In-browser automation executed against:

- `pages/TL.JJ.008/index.html`

Successful steps:

- page loaded
- local QA state reset
- no hang occurred

Last successful step:

- `load`

Blocking QA issue:

- headless in-browser automation consistently timed out while trying to open the Navigator panel from inside a same-origin iframe harness
- the same failure occurred in two separate harness attempts:
  - direct `element.click()`
  - synthetic `MouseEvent('click', ...)`

Interpretation:

- this did **not** isolate a confirmed Navigator UI regression
- because the blocker occurred before the first cockpit-mode transition, no additional manual-browser steps were marked as passed in this checkpoint

## Validation commands and results

Source asset validation:

```bash
node --check pipeline/13-ssg/static/js/navigator.js
node --check pipeline/13-ssg/static/js/navigator-store.js
```

Results:

- `navigator.js`: passed
- `navigator-store.js`: passed

Derived static-site validation:

```bash
node --check pipeline/13-static-site/js/navigator.js
node --check pipeline/13-static-site/js/navigator-store.js
```

Results:

- built `navigator.js`: passed
- built `navigator-store.js`: passed

Local QA servers used:

- temporary localhost static server
- temporary same-origin QA harness servers

Browser QA result:

- failed before Navigator panel could be opened by automation
- no feature patch was applied from this QA pass

## Known limitations

- a full click-through manual QA pass was not completed in this turn
- the browser automation environment could load the page but could not reliably transition the Navigator shell from closed to open from the QA harness
- because of that, these checklist items remain unconfirmed in this checkpoint:
  - pin flow end-to-end
  - path creation
  - add pin to path
  - add current page
  - reorder persistence
  - remove flow
  - export flow

## Safety guarantees

- no Canon changes
- no CSL changes
- no provider / ÑĀṆA script changes
- no `build.py` changes
- no template changes
- no deploy changes
- no secrets or credential files were read, printed, copied, or committed
- no backend or sync layer was introduced
- Study Paths remain:
  - local-only
  - user-defined
  - non-canonical
  - derived-only
  - reversible

## Rollback instructions

Revert Study Path Engine v1 source changes only:

```bash
git checkout -- pipeline/13-ssg/static/js/navigator.js
git checkout -- pipeline/13-ssg/static/css/navigator.css
```

Clear local browser state manually:

```js
localStorage.removeItem('axis.navigator.v1.pinned_answers');
localStorage.removeItem('axis.navigator.v1.study_paths');
```

If you also want to discard the refreshed derived static assets, rebuild or restore:

```bash
python3 pipeline/13-ssg/build.py
```

## Relationship to existing Navigator / ÑĀṆA layers

Study Path Engine v1 extends:

- `Validated Answer`
  - approved derivative answers become pinnable
- `Study Desk`
  - pinned answers become local study artifacts
- ÑĀṆA outputs
  - source for approved derivative answer metadata shown in BeYond Mode

It does **not** promote any derivative answer into Canon.
