# FlagFix 058 — Vitrine Visual Review Checklist

Date: 2026-05-19

## Scope

This sprint defines the visual review checklist for the synced Vitrine payload before any push, deploy, or Netlify action.

No local server was started.

## Current Published State

Published repo:

- path: `/home/sanghop/axis/axis-niddhi-published`
- branch: `main`
- status: `main...origin/main [ahead 1]`
- working tree: clean
- remote: `https://github.com/matikamata/axis-niddhi.git`

Current local published commit:

- short hash: `92f4c29`
- full hash: `92f4c298f17008f4022c0267f1e64af14a1742a1`
- message: `build(vitrine): sync static payload after title corrections`

## Static Parity

Comparison:

```bash
diff -qr \
  axis-niddhi-published/pipeline/13-static-site \
  axis-niddhi-production/pipeline/13-static-site
```

Result:

- output: `/tmp/flagfix_058_parity_diff_qr.txt`
- diff line count: 0
- published static payload still matches production static payload

## Local Review Paths

Static payload root:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Review these files directly or through a local server:

- archive/list page: `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/archive.html`
- site index: `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/index.html`
- search data: `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/search_index.json`
- index data: `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/index.json`
- LD.AA.000 page: `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/pages/LD.AA.000/index.html`
- BA.AA.004 page: `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/pages/BA.AA.004/index.html`
- Bodhi leaf asset: `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/assets/BodhiCircuitLeaf.png`

Suggested local review command only, not executed:

```bash
cd /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site
python3 -m http.server 8088
```

Suggested local URLs if the command is run in a future explicit review step:

- `http://localhost:8088/`
- `http://localhost:8088/archive.html`
- `http://localhost:8088/pages/LD.AA.000/`
- `http://localhost:8088/pages/BA.AA.004/`

## Visual Checklist

Archive/list page:

- [ ] `archive.html` loads without broken layout.
- [ ] Archive entries are readable on desktop width.
- [ ] Archive entries are readable on mobile/narrow width.
- [ ] The untranslated label reads `Awaiting translation / Aguardando tradução`.
- [ ] The old label `pending translation / pendente de tradução` is absent.

Title corrections:

- [ ] `pages/LD.AA.000/index.html` displays `Vivendo o Dhamma`.
- [ ] `Vivendo il Dhamma` is absent in visible title areas.
- [ ] `pages/BA.AA.004/index.html` displays `Vipariṇāma Two Meanings`.
- [ ] `Viparie1B987Ama Two Meanings` is absent in visible title areas.
- [ ] Previous/next/pathway links around LD.AA.000 and BA.AA.004 display corrected labels.

BodhiCircuitLeaf asset:

- [ ] The Bodhi leaf appears without the old white square background.
- [ ] The transparent/no-background asset blends correctly with page backgrounds.
- [ ] The image is crisp enough at expected display sizes.
- [ ] No obvious layout shift or oversized rendering appears.

Search/index behavior:

- [ ] Search UI opens and remains responsive if locally reviewable.
- [ ] Search/index entries for LD.AA.000 use `Vivendo o Dhamma`.
- [ ] Search/index entries for BA.AA.004 use `Vipariṇāma Two Meanings`.
- [ ] No stale title appears in search results.

Print preview spot check:

- [ ] Open print preview for `LD.AA.000`.
- [ ] Open print preview for `BA.AA.004`.
- [ ] Titles render correctly in print preview.
- [ ] The Bodhi asset does not introduce unwanted white background artifacts in print contexts.

Mobile/narrow viewport spot check:

- [ ] `archive.html` at narrow width does not overlap text.
- [ ] `LD.AA.000` title fits cleanly.
- [ ] `BA.AA.004` title fits cleanly with Pāli diacritic intact.
- [ ] Navigation controls remain usable.

## Text/Static Sanity Checks

Expected absent strings:

- `Vivendo il Dhamma`
- `Viparie1B987Ama Two Meanings`
- `pending translation / pendente de tradução`

Expected present strings:

- `Vivendo o Dhamma`
- `Vipariṇāma Two Meanings`
- `Awaiting translation / Aguardando tradução`

Expected asset:

- `assets/BodhiCircuitLeaf.png` should be the approved transparent/no-background version from commit `92f4c29`.

## Decision Gates

Pass:

- visual review passes;
- stale strings remain absent;
- corrected strings are visible;
- Bodhi asset looks correct;
- print/mobile spot checks do not reveal regressions.

Then proceed to a follow-up push/Netlify plan.

Fail:

- any stale title/label appears;
- the transparent Bodhi asset looks wrong;
- layout, print, or mobile review reveals visible regressions.

Then open a targeted FlagFix before any push/deploy/Netlify action.

## Proposed Next Sprint

Suggested #FlagFix_059:

- run the local server explicitly;
- perform visual review against the checklist;
- record pass/fail evidence;
- decide whether to push the published commit branch/PR or prepare manual Netlify handling.

## Non-Actions

This sprint did not:

- push from `axis-niddhi-published`;
- deploy;
- run build or pipeline;
- start a local server;
- call DeepL;
- translate anything;
- modify CSL;
- modify metadata CSVs;
- modify `Translation_Control_Center.csv`;
- modify SP10/SP11;
- copy or sync files;
- change `.gitignore`;
- modify `axis-niddhi-published`;
- modify production static.
