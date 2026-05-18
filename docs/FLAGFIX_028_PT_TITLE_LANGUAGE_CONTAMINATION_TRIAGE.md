# FLAGFIX_028 - PT Title Language Contamination Triage

Date: 2026-05-18
Scope: read-only triage plus this report
Observed production URL: https://niddhi.netlify.app/pages/ld.aa.000/

## Summary

The reported PT title contamination is confirmed.

For `LD.AA.000`, the English title is:

```text
Living Dhamma
```

The PT title currently stored in canonical AXIS metadata is:

```text
Vivendo il Dhamma
```

The Italian article `il` is present in the `titles.pt` field for `LD.AA.000`. The local static output also contains the same string, which indicates the renderer is faithfully consuming already-contaminated metadata rather than inventing the title.

## Branch and State

Commands run:

```bash
git status -sb
git log --oneline --decorate -n 8
```

Observed state:

```text
## main...origin/main
```

Recent HEAD:

```text
d0a29b9b (HEAD -> main, tag: checkpoint/buteco-reforma-closed-v2-20260518, origin/main, origin/HEAD) docs: update Buteco closing summary with Netlify SOP
9b834fcc (tag: checkpoint/netlify-refresh-sop-20260518) docs: add production to published Netlify refresh SOP
77290ac6 (tag: checkpoint/buteco-reforma-closed-20260518) docs: add Buteco reform closing summary
f365c60c (tag: checkpoint/pr-discipline-guide-20260518) docs: add PR discipline guide
ec40f172 (tag: checkpoint/bee-first-task-issue-flow-20260518) docs: link bee first task to issue flow
ca6fc990 (tag: checkpoint/cloudflare-routing-note-20260518) docs: record Cloudflare routing note
9a4a161a (tag: checkpoint/static-payload-gitignore-hygiene-20260518) chore: allow approved Cloudflare static payload files
25613dcb docs: generalize local paths in Netlify refresh plan
```

## Sprint Number Check

`docs/FlagFix/` currently contains FlagFix documents through `FLAGFIX_027_AUDIO_PLAYBACK_APPLE_DEVICES.md`.

There is no `FLAGFIX_028...` file in `docs/FlagFix/`.

Conclusion: `028` is the correct next sequential sprint number for this triage. Note: `FLAGFIX_026` is not present in the current `docs/FlagFix/` listing, but the highest existing numbered sprint is `027`, so `028` is still the next unused number after the latest materialized sprint.

## Files Inspected

Primary target files:

```text
pipeline/09-csl/LD.AA.000/meta/identity.json
pipeline/09-csl/LD.AA.000/meta/identity.json.bak
pipeline/09-csl/LD.AA.000/source/en-US/content.html
pipeline/09-csl/LD.AA.000/source/pt-BR/content.html
pipeline/13-static-site/pages/LD.AA.000/index.html
pipeline/13-static-site/index.json
pipeline/13-static-site/search_index.json
review/title-matrix/flagfix_020_title_comparison_matrix.csv
docs/FlagFix/FLAGFIX_020_TITLE_COMPARISON_MATRIX.md
```

Checked but not found:

```text
pipeline/13-static-site/pages/ld.aa.000/index.html
```

Supporting corpus checks:

```text
pipeline/09-csl/*/meta/identity.json
pipeline/03-translations/
pipeline/09-csl/
pipeline/13-static-site/
docs/
review/
```

## Exact Occurrence of "Vivendo il Dhamma"

Confirmed exact occurrences:

```text
pipeline/09-csl/LD.AA.000/meta/identity.json:19:    "pt": "Vivendo il Dhamma",
pipeline/13-static-site/pages/LD.AA.000/index.html:88:    <h1 class="title-pt">Vivendo il Dhamma</h1>
pipeline/13-static-site/index.json:4011:          "title_pt": "Vivendo il Dhamma",
pipeline/13-static-site/search_index.json:4762:    "title_pt": "Vivendo il Dhamma",
```

The broad requested search:

```bash
grep -RIn "Vivendo il Dhamma\|Living Dhamma" pipeline/ docs/ review/ 2>/dev/null
```

returned many legitimate `Living Dhamma` body/reference hits across the corpus. The only canonical `Vivendo il Dhamma` source occurrence identified is the `LD.AA.000` identity metadata; the static-site hits are generated downstream artifacts.

## LD.AA.000 Source Comparison

`pipeline/09-csl/LD.AA.000/meta/identity.json`:

```json
"titles": {
  "en": "Living Dhamma",
  "en_source": "legacy_migration",
  "pt": "Vivendo il Dhamma",
  "pt_source": "deepl_v5"
}
```

`pipeline/09-csl/LD.AA.000/source/en-US/content.html` contains legitimate English body headings such as:

```text
Living Dhamma - Overview
Living Dhamma - Fundamentals
```

`pipeline/09-csl/LD.AA.000/source/pt-BR/content.html` does not contain `Vivendo il Dhamma`. It contains PT body headings such as:

```text
Dhamma Vivo - Visao Geral
Dhamma Vivo - Fundamentos
```

The local static page contains:

```html
<h1 class="title-en">Living Dhamma</h1>
<h1 class="title-pt">Vivendo il Dhamma</h1>
```

This supports metadata-root contamination, not body-wide contamination.

## Italian Pattern Audit

Patterns requested:

```text
" il "
" lo "
" gli "
" della "
" del "
" delle "
" degli "
" nell"
" sull"
"Vivendo il"
```

Focused audit of `titles.pt` across 748 CSL identity files found only:

```text
LD.AA.000    Living Dhamma    Vivendo il Dhamma
```

No other `titles.pt` field matched the requested Italian markers in the focused metadata-title audit.

The broad body search for these small tokens is noisy and not reliable as a title-risk signal because many substrings can occur inside Portuguese words, URLs, English retained quotations, source links, and HTML attributes. For this issue, the actionable contaminated title scope is the identity title layer.

## Root Cause Assessment

Most likely root cause:

```text
pipeline/09-csl/LD.AA.000/meta/identity.json -> titles.pt
```

The metadata records:

```text
pt_source: deepl_v5
```

Probable failure mode: a DeepL-derived or title-translation-layer value introduced Italian `il` into the PT title during metadata/title generation.

Not likely root causes:

- `source/pt-BR/content.html`: does not contain `Vivendo il Dhamma`.
- `source/en-US/content.html`: contains legitimate English source text only.
- renderer/template: static output reflects the metadata value exactly.
- CSS/JS/static behavior: no evidence that styling or client logic changes the title text.
- stale static output alone: static output is stale relative to any future fix, but it currently matches the canonical contaminated metadata.

## Scope

Current evidence points to a single-post title metadata issue:

```text
LD.AA.000
```

Corpus-wide title scan across `pipeline/09-csl/*/meta/identity.json` did not find additional `titles.pt` values matching the requested Italian contamination markers.

Generated static artifacts also contain the contaminated value for `LD.AA.000`, but those appear downstream of the canonical metadata, not independent sources.

## Minimum Correction Proposal

Do not correct blindly in this triage step.

Recommended next implementation step, after approval:

1. Add `LD.AA.000` to the title review workflow/matrix with issue type similar to `pt_title_language_contamination`.
2. Human-review the preferred PT title. Candidate forms visible from current corpus context:
   - `Dhamma Vivo`
   - `Vivendo o Dhamma`
3. Apply the approved PT title only to:
   - `pipeline/09-csl/LD.AA.000/meta/identity.json`
4. Rebuild/regenerate static artifacts only after metadata correction is approved.
5. Verify that the generated outputs update:
   - `pipeline/13-static-site/pages/LD.AA.000/index.html`
   - `pipeline/13-static-site/index.json`
   - `pipeline/13-static-site/search_index.json`

No renderer, CSS, JS, deploy config, Cloudflare config, or Netlify config changes are indicated by this triage.

## Rollback

If the correction is applied and must be reverted:

1. Revert the single metadata title change in:

```text
pipeline/09-csl/LD.AA.000/meta/identity.json
```

2. Re-run the same static generation step used for the approved correction, so generated output returns to the previous metadata-derived title.
3. If the change is committed, rollback can be a normal `git revert <commit>` of the metadata/static-output correction commit.

Because the likely fix is isolated to one metadata field plus generated artifacts, rollback should be low-risk if kept out of renderer/template/deploy code.

## GitHub Issue Recommendation

Yes, open a GitHub issue if this sprint follows the repository's issue discipline.

Suggested issue title:

```text
FLAGFIX_028: Correct PT title language contamination for LD.AA.000
```

Suggested issue scope:

- confirm human-approved PT title for `Living Dhamma`;
- record `Vivendo il Dhamma` as Italian contamination in `titles.pt`;
- authorize a single metadata correction;
- authorize static regeneration only after metadata fix approval;
- explicitly exclude renderer, CSS, JS, Cloudflare, Netlify, and broad CSL rewrites.

## Triage Conclusion

`FLAGFIX_028` is valid as the next sprint number. The defect is real and localized: `LD.AA.000` has Italian contamination in the PT metadata title. The rendered/local static outputs are downstream reflections of that metadata.

No build or pipeline was run during this triage. No deploy config, renderer, CSS, JS, CSL body content, or static output was modified.
