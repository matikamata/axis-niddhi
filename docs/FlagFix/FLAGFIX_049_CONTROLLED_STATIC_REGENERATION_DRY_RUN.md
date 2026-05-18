# FlagFix 049 - Controlled Static Regeneration Dry Run

Date: 2026-05-18

## Scope

This sprint performed a controlled static regeneration dry run in the development/production workspace.

No Netlify/Vitrine promotion, deploy, DeepL call, translation, CSL edit, metadata CSV edit, `Translation_Control_Center.csv` edit, SP10/SP11 edit, apply script, `.gitignore` change, or commit was performed.

## Preflight Validators

CSL correction manifest validator:

```text
summary: total=25 match=25 mismatch=0 missing_file=0 missing_path=0
manifest_validator_exit_code=0
```

PT title language audit:

```text
checked=748
null_pt_titles=439
hits=0
pt_title_language_audit_exit_code=0
```

## Static Regeneration Command

Command used:

```bash
python3 pipeline/13-ssg/build.py
```

The command was identified as the standard SSG engine from `pipeline/13-ssg/build.py`. The compatibility shim `SD03_static_site_build.py` delegates to `build.py`, but the full pipeline was not run.

Build result:

- posts total: 748
- rebuilt: 748
- skipped: 0
- errors: 0
- output: `pipeline/13-static-site`
- build id: `a53b5f1f1b74e63a`

## Diff Summary

Diff stat after regeneration:

```text
348 files changed, 1343 insertions(+), 1337 deletions(-)
```

Changed path categories:

- total changed paths: 348
- static output paths: 347
- SSG cache paths: 1
- other paths: 0

Changed non-static generated/cache file:

- `pipeline/13-ssg/cache/build_state.json`

No unexpected source paths were modified. In particular, there were no tracked changes to:

- `pipeline/09-csl/**`
- `pipeline/metadata/Translation_Control_Center.csv`
- SP10/SP11 scripts
- `.gitignore`
- `/home/sanghop/axis/axis-niddhi-published`

## Stale String Check

Post-regeneration search for stale strings returned no matches:

```text
Vivendo il Dhamma: 0
Viparie1B987Ama Two Meanings: 0
pending translation / pendente de tradução: 0
```

## Corrected String Check

Corrected strings now appear in generated static artifacts:

- `pipeline/13-static-site/index.json` contains `Vipariṇāma Two Meanings`.
- `pipeline/13-static-site/search_index.json` contains `Vipariṇāma Two Meanings`.
- `pipeline/13-static-site/pages/BA.AA.004/index.html` contains `Vipariṇāma Two Meanings` in page title and H1.
- `pipeline/13-static-site/index.json` contains `Vivendo o Dhamma`.
- `pipeline/13-static-site/search_index.json` contains `Vivendo o Dhamma`.
- `pipeline/13-static-site/pages/LD.AA.000/index.html` contains `Vivendo o Dhamma` in the PT H1.
- `pipeline/13-static-site/archive.html` contains `Awaiting translation / Aguardando tradução`.

## Focused Diff Evidence

`LD.AA.000`:

```diff
-    <h1 class="title-pt">Vivendo il Dhamma</h1>
+    <h1 class="title-pt">Vivendo o Dhamma</h1>
```

`BA.AA.004`:

```diff
-    <title>Viparie1B987Ama Two Meanings | AXIS-NIDDHI</title>
+    <title>Vipariṇāma Two Meanings | AXIS-NIDDHI</title>

-    <h1 class="title-en">Viparie1B987Ama Two Meanings</h1>
+    <h1 class="title-en">Vipariṇāma Two Meanings</h1>
```

Index/search/archive examples:

```diff
-          "title_en": "Viparie1B987Ama Two Meanings",
+          "title_en": "Vipariṇāma Two Meanings",

-          "title_pt": "Vivendo il Dhamma",
+          "title_pt": "Vivendo o Dhamma",
```

## Review Notes

The diff is broad because the SSG rebuilt all 748 posts after detecting template/cache changes. Many modified pages have small generated changes, often title/pathway/index updates or regenerated build metadata.

Before commit:

- review `git diff --stat`;
- review `git diff --name-status`;
- inspect `archive.html`, `index.json`, and `search_index.json`;
- inspect representative pages from #028 and #037-#043;
- rerun stale string checks;
- confirm no unexpected source files are modified.

## Recommendation

Recommendation before commit:

- Do not promote Vitrine yet.
- Do not deploy.
- Treat this as a reviewable static regeneration candidate.
- Commit only after human review of the broad generated diff.

The regeneration appears internally consistent: validators passed, stale strings disappeared, corrected strings appeared, and changed paths are limited to generated static output plus SSG cache state.

## No-Change Confirmations

- Did not touch `/home/sanghop/axis/axis-niddhi-published`.
- Did not update Netlify/Vitrine.
- Did not deploy.
- Did not call DeepL.
- Did not translate anything.
- Did not modify CSL content.
- Did not modify metadata CSVs.
- Did not modify `Translation_Control_Center.csv`.
- Did not modify SP10/SP11 behavior.
- Did not create an apply script.
- Did not change `.gitignore`.
- Did not commit.
