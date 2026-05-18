# FlagFix 048 - Static Regeneration Readiness Checklist

Date: 2026-05-18

## Scope

This sprint created a read-only readiness checklist for a future static regeneration batch.

No build, pipeline, deploy, DeepL call, translation, CSL edit, static edit, metadata CSV edit, `.gitignore` change, apply script, Netlify update, or Vitrine promotion was performed.

## Current Preflight Results

CSL correction manifest validator:

```text
summary: total=25 match=25 mismatch=0 missing_file=0 missing_path=0
manifest_validator_exit_code=0
```

PT title language contamination audit:

```text
checked=748
null_pt_titles=439
hits=0
pt_title_language_audit_exit_code=0
```

These two validators must pass before any future regeneration.

## Static Spot Checks

Read-only stale-string search found stale generated artifacts:

- `pipeline/13-static-site/index.json` still contains `Viparie1B987Ama Two Meanings`.
- `pipeline/13-static-site/search_index.json` still contains `Viparie1B987Ama Two Meanings`.
- `pipeline/13-static-site/pages/BA.AA.004/index.html` still contains `Viparie1B987Ama Two Meanings`.
- `pipeline/13-static-site/archive.html` still contains `Viparie1B987Ama Two Meanings`.
- `pipeline/13-static-site/index.json` still contains `Vivendo il Dhamma`.
- `pipeline/13-static-site/search_index.json` still contains `Vivendo il Dhamma`.
- `pipeline/13-static-site/pages/LD.AA.000/index.html` still contains `Vivendo il Dhamma`.
- related pathway snippets still contain stale `Vivendo il Dhamma` or `Viparie1B987Ama Two Meanings`.

Corrected-string search found:

- `Awaiting translation / Aguardando tradução` already appears in `pipeline/13-static-site/archive.html`.
- `Vivendo o Dhamma` appears in some existing static body/pathway contexts.
- The corrected title `Vipariṇāma Two Meanings` was not observed in the checked generated title artifacts, confirming static title staleness remains.

## Likely Future Regeneration Command

Do not run in this sprint.

The likely direct SSG command is:

```bash
python3 pipeline/13-ssg/build.py
```

The compatibility shim indicates equivalent emergency usage from inside the SSG directory:

```bash
cd pipeline/13-ssg
python3 SD03_static_site_build.py
```

Because this project has several pipeline wrappers, the exact regeneration command should be confirmed in the approved regeneration sprint before execution.

## Pre-Regeneration Checklist

Before static regeneration:

- Confirm branch and clean tracked state with `git status -sb`.
- Run `python3 pipeline/scripts/tools/validate_csl_correction_manifest.py`.
- Confirm manifest validator summary is `total=25 match=25 mismatch=0 missing_file=0 missing_path=0`.
- Run `python3 pipeline/scripts/tools/audit_pt_titles_language_contamination.py`.
- Confirm PT title language audit has `hits=0`.
- Confirm no apply script is needed because local CSL already matches manifest.
- Confirm `pipeline/09-csl` local state is the intended source for regeneration.
- Confirm no Netlify/Vitrine promotion is bundled with the regeneration.

## Expected Changed Artifacts

If static is regenerated from corrected local CSL, expected generated output changes may include:

- `pipeline/13-static-site/pages/*/index.html`
- `pipeline/13-static-site/archive.html`
- `pipeline/13-static-site/index.json`
- `pipeline/13-static-site/search_index.json`
- `pipeline/13-static-site/build_meta.json`
- SSG cache/build metadata if the generator updates it
- generated copied assets only if the build process refreshes them

Generated static diffs may be broad. Review should focus on title metadata and known generated indexes first.

## Expected String Changes

Stale strings that should disappear from generated title/index surfaces:

- `Vivendo il Dhamma`
- `Viparie1B987Ama Two Meanings`
- remaining ASCII/hex-like title artifacts from #037-#043

Corrected strings that should appear in generated title/index surfaces:

- `Vivendo o Dhamma`
- `Vipariṇāma Two Meanings`
- corrected EN titles from #039-#042
- corrected PT titles from #043
- `Awaiting translation / Aguardando tradução`

## Post-Regeneration Diff Review Checklist

After regeneration, before commit/push/merge:

- Run the CSL correction manifest validator again.
- Run the PT title language audit again.
- Search static for stale strings:

```bash
grep -RIn "Vivendo il Dhamma\|Viparie1B987Ama\|pending translation / pendente de tradução" pipeline/13-static-site 2>/dev/null
```

- Search static for corrected strings:

```bash
grep -RIn "Vivendo o Dhamma\|Vipariṇāma Two Meanings\|Awaiting translation / Aguardando tradução" pipeline/13-static-site 2>/dev/null
```

- Review `git diff --stat` for unexpected broad changes.
- Review representative files for `LD.AA.000`, `BA.AA.004`, and one title from each correction batch.
- Review `archive.html`, `index.json`, and `search_index.json`.
- Do not include unrelated renderer/template/CSS/JS changes unless explicitly approved.
- Do not commit static output unless the operator explicitly approves generated static changes.

## Netlify/Vitrine Separation

Cloudflare/dev and Netlify/Vitrine must remain separate.

- `/home/sanghop/axis/axis-niddhi-production` is the Cloudflare/dev/experimental workspace.
- `/home/sanghop/axis/axis-niddhi-published` is the approved Netlify Vitrine workspace.

Static regeneration in production workspace does not automatically authorize promotion to Vitrine.

## Vitrine Promotion Checklist

Before promoting to `/home/sanghop/axis/axis-niddhi-published`:

- Confirm reviewed static regeneration is approved.
- Confirm generated static diff contains only expected site output.
- Confirm no stale title strings remain in generated static.
- Confirm corrected title strings appear in page HTML, archive, index JSON, and search index.
- Confirm local preview/QA has been completed if requested.
- Confirm explicit operator approval for Netlify/Vitrine promotion.
- Keep promotion as a separate step from regeneration.

## Recommendation

Recommended sequence:

1. Keep #048 as documentation only.
2. In a future approved sprint, run preflight validators first.
3. Regenerate static in the dev/production workspace only.
4. Review static diffs and stale-string searches.
5. Promote to Netlify/Vitrine only in a separate approved step after review.

## Explicit Non-Actions

- Did not touch `/home/sanghop/axis/axis-niddhi-published`.
- Did not update Netlify/Vitrine.
- Did not run build, pipeline, or deploy.
- Did not call DeepL.
- Did not translate anything.
- Did not modify CSL content.
- Did not modify static artifacts.
- Did not modify metadata CSVs.
- Did not modify `Translation_Control_Center.csv`.
- Did not modify SP10/SP11 behavior.
- Did not create an apply script.
- Did not change `.gitignore`.
