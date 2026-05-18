# AXIS-NIDDHI — Post DeepL / Showcase Publication Handoff

**Date:** 2026-05-12  
**Audience:** CodeX, Claude, Gemini, future IDE agents  
**Scope:** Operational handoff after the 309 pt-BR showcase publication cycle  
**Status:** Current publication cycle closed; DeepL quota exhausted until the next reset window.

---

## 1. Executive summary

The current AXIS-NIDDHI showcase has been translated, frozen, built, published to Git/Cloudflare, and synchronized to the manual Netlify publish surface.

Current known state:

| Item | State |
|---|---|
| Total corpus posts | 748 |
| pt-BR posts available after this cycle | 309 |
| Translation menu state | 309 `DONE`, 439 `PENDING`, 0 `COMMAND=YES` |
| Manual Netlify checkpoint | `checkpoint/showcase-309-ptbr-published-20260512` |
| Current user-facing preferred surface | Netlify + GitHub repo, with GitHub Pages as backup |
| Cloudflare role | Feature/testing surface unless/until audio publish strategy is improved |
| DeepL state | quota exhausted; pause translation until next reset window |

The important architectural lesson from this cycle is:

> **`axis-niddhi-production` is the active canonical working/publish source. `axis-niddhi-published` is the manual deployment mirror for Netlify drag-and-drop, not the place where translation/build work happens.**

---

## 2. Workspace roles

### `/home/sanghop/axis/axis-niddhi-production`

This is now the **active production workspace**.

Use it for:

- DeepL translation operations.
- `SP00` freeze.
- `SP09` menu regeneration.
- `SP10` DeepL execution.
- `build.py` local showcase generation.
- Git branches / PRs / tags.
- Final source for synchronizing the manual Netlify publish surface.

Normal branch discipline still applies. Recommended branch families:

```text
prep/deepl-...
deepl/batch-...
publish/showcase-...
docs/...
```

### `/home/sanghop/axis/axis-niddhi-published`

This is the **manual publish mirror**.

Use it for:

- A local, full static artifact directory that can be dragged to Netlify.
- Keeping the published package complete, including local generated audio files that Git-based deploys may omit.
- Manual deployment preparation only.

Do **not** use it for:

- DeepL.
- `SP00`.
- `SP09`.
- `SP10`.
- Build experimentation.
- Pipeline development.
- Translation governance.

The authoritative source for updating this directory is:

```text
/home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/
```

The intended target is:

```text
/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/
```

### Real lab / archaeology spaces

Lab and archaeology remain outside the active publication path:

```text
/home/sanghop/bengyond-playground/pipeline
/media/sanghop/BrasileirinhoHD/20260427_16h16_Quartinho-da-BOA-bagunça
Zibaldone folders
```

Use those for archaeology, rescue, experiments, and future feature recovery.  
Do **not** depend on them for current operational secrets or current production translation work.

---

## 3. Translation workflow that worked

### Step A — Human selection

The human operator selects the next posts by editing:

```text
pipeline/metadata/Translation_Control_Center.csv
```

and marking intended rows:

```text
COMMAND=YES
```

Agents must not invent the selection order. The user owns the sequence.

Before running DeepL, validate:

```text
DONE selected = 0
YES count is intentional
selected chars are understood
private key exists
```

### Step B — Run DeepL only via `SP10`

Run:

```bash
python3 pipeline/scripts/core/SP10_translate_deepl.py
```

Expected behavior:

- Reads only rows with `COMMAND=YES`.
- Skips `DONE`.
- Writes new pt-BR body files into:

```text
pipeline/09-csl/<PDPN>/source/pt-BR/content.html
```

If DeepL returns:

```text
HTTP 456: {"message":"Quota exceeded"}
```

stop calmly. This is expected when a selected batch exceeds quota.

### Step C — Freeze translations

After `SP10`, dry-run first:

```bash
python3 pipeline/scripts/core/SP00_freeze_translations.py
```

Then apply:

```bash
python3 pipeline/scripts/core/SP00_freeze_translations.py --apply
```

Purpose:

- Copy `09-csl/<PDPN>/source/pt-BR/content.html` into `03-translations/<PDPN>/pt-BR.html`.
- Generate/update `translation.json`.
- Regenerate `03-translations/manifest.json`.

### Step D — Regenerate translation menu

Run:

```bash
python3 pipeline/scripts/core/SP09_translation_menu.py
```

Expected result:

- `DONE` count matches pt-BR count.
- `PENDING` count is the remainder.
- `COMMAND` resets to blank for all rows.

After the 309 pt-BR cycle, expected menu state:

```text
DONE: 309
PENDING: 439
COMMAND=YES: 0
```

### Step E — Build local showcase

Run only after freeze/menu are aligned:

```bash
cd /home/sanghop/axis/axis-niddhi-production/pipeline/13-ssg
python3 build.py
```

Expected successful build characteristics:

```text
Posts total: 748
Posts PT-BR: 309 / 748
Errors: 0
search_index_count: 748
```

### Step F — Publish through PR

Generated static-site output is guarded. Do not commit it unless the user explicitly approves publication of the exact build.

Minimum publication package:

```text
pipeline/13-static-site/**
```

Exclude:

```text
pipeline/13-ssg/cache/build_state.json
pipeline/09-csl/**
pipeline/03-translations/**
pipeline/metadata/**
pipeline/scripts/private/**
```

---

## 4. Git policy observed in this cycle

### Versioned

The publication PR for the 309 pt-BR static preview included only:

```text
pipeline/13-static-site/**
```

The translation menu refresh PR included only:

```text
pipeline/metadata/Translation_Control_Center.csv
```

### Not versioned / operational

These remain operational/generated layers and may not appear in Git diffs:

```text
pipeline/09-csl/**
pipeline/03-translations/**
pipeline/13-ssg/cache/**
pipeline/scripts/private/**
```

### Private files

The operational DeepL key lives at:

```text
pipeline/scripts/private/deepl_key.txt
```

Private files must stay ignored:

```text
pipeline/scripts/private/*
!pipeline/scripts/private/.gitkeep
```

Never print, quote, commit, or expose key contents.

---

## 5. Publication surfaces

### Netlify

Netlify is the preferred end-user surface for now because manual full-folder deploy preserves the complete local artifact tree, including audio.

For manual Netlify deploy, drag/copy this directory:

```text
/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site
```

Important: publish the **site directory itself**, not the repo root.

### Cloudflare Pages

Cloudflare remains useful for testing and feature preview, but its Git-based deploy does not currently include ignored local MP3 assets under:

```text
pipeline/13-static-site/assets/audio/
```

Therefore, audio may fail on Cloudflare/Safari-style clients if the asset is missing and an HTML fallback is returned.

Do not spend more time on this during DeepL quota exhaustion unless explicitly reopening `FLAGFIX_027`.

### GitHub Pages

GitHub Pages is a backup/static reference surface. It should not replace Netlify as the full audio-complete user-facing surface unless the artifact strategy is explicitly changed.

---

## 6. Production → Published synchronization strategy

After a publication PR is merged and production `main` is clean, synchronize the full static site into the manual published mirror.

Dry-run first:

```bash
rsync -avhn --delete --itemize-changes \
  /home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/ \
  /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/
```

If sane, real sync:

```bash
rsync -avh --delete --itemize-changes \
  /home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/ \
  /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/
```

Validate:

```bash
test -f /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/archive.html
test -f /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/search_index.json
test -f /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/pages/LD.CC.005/index.html
find /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/assets/audio -type f -name '*.mp3' | wc -l
```

Expected after the 309 pt-BR sync:

```text
MP3 count: 463
LD.CC.005 checksum matches production
archive/search_index/pages exist
```

The `published` workspace will naturally show many modified files after rsync. That is acceptable because it is a manual publish mirror, not the source of truth.

---

## 7. Known open issues / future FlagFix candidates

### `FLAGFIX_027` — Audio delivery on Cloudflare / Apple devices

Current decision:

- Do not block the translation workflow on this.
- Netlify manual full-folder deploy is the end-user surface for now.
- Cloudflare can remain a feature/testing surface.
- Preserve the existing rule: local small audio stays local; only audio over 25 MiB is externalized.

Future route:

- Investigate Cloudflare direct artifact deploy or alternate media origin.
- Do not rewrite all audio to external URLs.
- Do not change player logic before proving asset-delivery failure.

### H5 / typography inconsistencies

Known issue appears in `BD.AA.002` and other pages.

Decision:

- Do not block 309 pt-BR publication.
- Create or reuse a later FlagFix after translation quota work stabilizes.

### Translation archaeology gap

Earlier there was confusion between pt-BR entries in `09-csl` and `03-translations`. This cycle repaired the active state:

```text
09-csl pt-BR: 309
03-translations: 309
Translation_Control_Center DONE: 309
```

There may still be older translated material in archaeology folders. Do not mix archaeology into the active pipeline during a quota-sensitive cycle unless explicitly requested.

---

## 8. Agent behavior rules for the next session

Before doing anything, agents should report:

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git status -sb
git log --oneline -5
```

Then check:

```bash
find pipeline/09-csl -path "*/source/pt-BR/content.html" | wc -l
find pipeline/03-translations -mindepth 1 -maxdepth 1 -type d | wc -l
```

And inspect the CSV counts:

```text
DONE
PENDING
COMMAND=YES
DONE_WITH_YES
```

Agents must not:

- Run `SP10` unless `COMMAND=YES` rows are intentionally selected by the user.
- Run `SP09` before understanding whether user selections should be preserved.
- Commit `pipeline/13-static-site/**` without explicit publication approval.
- Touch private keys beyond checking file existence and ignore status.
- Use `/home/sanghop/bengyond-playground` as an operational dependency for current production.
- Treat `axis-niddhi-published` as the place to translate/build.
- Invent a post order for DeepL; the human operator selects rows.

Agents may:

- Ask the user to select or confirm rows.
- Validate counts.
- Create safety tags.
- Run `SP00` dry-run/apply after DeepL.
- Run `SP09` after freeze.
- Build local showcase after freeze/menu alignment.
- Prepare narrow PRs with explicit file scopes.

---

## 9. Current stopping point

We are stopped cleanly because:

- The 309 pt-BR static preview was merged.
- The manual Netlify surface was synchronized.
- A checkpoint tag was pushed for the manual publication surface.
- DeepL quota is exhausted until the next reset window.
- The printed review batch is already with the reviewer.
- No urgent publication blocker remains.

Recommended next action when quota returns:

1. Start from `axis-niddhi-production`.
2. Confirm `main` is clean and current.
3. Confirm pt-BR/freeze/menu counts.
4. Human selects next `COMMAND=YES` rows.
5. Validate key and selected character count.
6. Run `SP10`.
7. Freeze with `SP00`.
8. Regenerate with `SP09`.
9. Build local showcase.
10. Publish via scoped PR.
11. Sync production static-site to published static-site for Netlify drag-and-drop.

---

## 10. One-line architecture mantra

> **Production builds the flower. Published carries the flower to the altar. Lab is where we study soil, seeds, weather, and tools.**
