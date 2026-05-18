# FLAGFIX_029 - Translation/title pipeline encoding and temporary-script retirement audit

Date: 2026-05-18
Workspace: `/home/sanghop/axis/axis-niddhi-production`
Mode: read-only triage plus this report

## Repository state

Commands run:

```bash
git switch main
git pull --ff-only origin main
git status -sb
git log --oneline --decorate -n 12
```

Observed:

```text
Already on 'main'
Your branch is up to date with 'origin/main'.
Already up to date.
## main...origin/main
```

Recent HEAD:

```text
456f43f8 (HEAD -> main, origin/main, origin/HEAD) Merge pull request #121 from matikamata/flagfix-028-pt-title-language-contamination
c0e11221 docs(flagfix): triage PT title language contamination
d0a29b9b docs: update Buteco closing summary with Netlify SOP
9b834fcc docs: add production to published Netlify refresh SOP
77290ac6 docs: add Buteco reform closing summary
f365c60c docs: add PR discipline guide
ec40f172 docs: link bee first task to issue flow
ca6fc990 docs: record Cloudflare routing note
9a4a161a chore: allow approved Cloudflare static payload files
25613dcb docs: generalize local paths in Netlify refresh plan
bdde860b docs: add Netlify refresh plan
d393e3b9 build: add contributor gateway dedication
```

## Scripts inventoried

The full requested inventory command also listed many `pipeline/03-translations/*/translation.json` artifacts and git refs. The script subset relevant to translation/title/DeepL/glossary handling is:

```text
pipeline/scripts/core/SA03_translation_progress.py
pipeline/scripts/core/SP00_freeze_translations.py
pipeline/scripts/core/SP01b_restore_translations.py
pipeline/scripts/core/SP07_compile_glossary.py
pipeline/scripts/core/SP08_glossary_gate.py
pipeline/scripts/core/SP09_translation_menu.py
pipeline/scripts/core/SP10_translate_deepl.py
pipeline/scripts/core/SP11_translate_titles.py
pipeline/scripts/legacy/04_compile_glossary.py
pipeline/scripts/legacy/05_translate_pilot_v5_surgeon.py
pipeline/scripts/legacy/05a_upload_glossary_deepl.py
pipeline/scripts/legacy/14_sync_titles_from_ledger.py
pipeline/scripts/legacy/S10_execute_translation_deepl.py
pipeline/scripts/private/deepl_key.txt
pipeline/scripts/tools/rebuild_translation_status.py
```

Credential note: `pipeline/scripts/private/deepl_key.txt` appeared in path inventory only. Its contents were not inspected.

Additional related utilities inspected or flagged:

```text
pipeline/scripts/core/SP02_upgrade_identity.py
pipeline/scripts/core/SP13_remediate_buda.py
pipeline/scripts/core/sanitize_pt.py
pipeline/scripts/tools/run_sp11_and_report.sh
pipeline/scripts/core/run_full_pipeline.sh
pipeline/scripts/legacy/07b_execute_menu_v3_guardian.py
pipeline/scripts/legacy/sp12_guardian/sp12_logic.py
```

## PT title ownership

Two core scripts can write `titles.pt`:

1. `pipeline/scripts/core/SP10_translate_deepl.py`
   - Translates EN title and EN body in the same post-processing flow.
   - Writes:

```python
data["titles"]["pt"] = title_pt
data["titles"]["pt_source"] = "deepl_v5"
```

2. `pipeline/scripts/core/SP11_translate_titles.py`
   - Dedicated title-only script.
   - Processes posts that already have PT content but are missing a PT title.
   - Writes:

```python
identity["titles"]["pt"] = pt_title
identity["titles"]["pt_source"] = "deepl_v5_sp11"
```

`SP02_upgrade_identity.py` preserves a non-empty existing `titles.pt` during `--force`, so it is not the likely source of the contamination.

## FLAGFIX_028 relationship

The `LD.AA.000` contaminated title had:

```text
pt_source: deepl_v5
```

That source marker points more strongly to the `SP10_translate_deepl.py` initial translation path than to `SP11_translate_titles.py`, because SP11 marks title output as `deepl_v5_sp11`.

Conclusion: the `LD.AA.000` case currently looks like a one-off DeepL translation artifact captured by SP10, not a proven systemic SP11 bug.

## SP11 safety for next batch

`SP11_translate_titles.py` is reasonably safe in write scope:

- dry-run by default;
- `--apply` required for writes;
- only touches `identity.json`;
- does not edit PT body content;
- uses UTF-8 reads/writes;
- uses `atomic_write_json`;
- sends title strings to DeepL in batches;
- sanitizes known Pali/Portuguese term drift through `sanitize_pt_output`.

However, it is not safe as a fully unattended next-batch title gate yet. Gaps found:

- No post-DeepL language contamination guard for Italian fragments such as ` il `, ` lo `, ` della `, etc.
- No human-review/matrix gate before accepting title output.
- No preflight report of proposed title translations before apply, beyond showing the first 10 EN titles in dry-run.
- No explicit allowlist/protection for known section titles such as `Living Dhamma`.
- It depends on DeepL output quality for short titles, where wrong-language artifacts are plausible.

Recommendation: SP11 can be used for dry-run inventory, but before any `--apply` batch it should gain a title QA gate or be wrapped by a post-translation title audit that blocks known language-contamination markers.

## Encoding risks

Most core scripts consistently use `encoding="utf-8"` for JSON, HTML, CSV, and logs.

Specific risks found:

1. User-provided metadata contamination scanner is not null-safe.

The requested Python command failed when it encountered `titles.pt: null`:

```text
AttributeError: 'NoneType' object has no attribute 'lower'
```

After adding a local read-only `None` guard, the scan completed:

```text
checked=748
null_pt=439
hits=0
```

This is not a corpus corruption, but it is a scriptlet hardening issue before reuse.

2. `SD01_generate_asset_map.py` reads HTML with `errors="ignore"`.

```text
html.read_text(encoding="utf-8", errors="ignore")
```

This can hide mojibake or invalid byte sequences. It is asset-map related, not title translation, but should be avoided for corruption audits.

3. `DI00_sql_vs_csl_audit.py` and `MI99_mission_report.py` use `errors="replace"` for audit/report reads.

This is acceptable for resilient reporting, but it can mask exact bad bytes. Not a title writer.

4. Legacy scripts include direct `open(..., encoding="utf-8")` writes without current atomic utilities.

Examples include:

```text
pipeline/scripts/legacy/14_sync_titles_from_ledger.py
pipeline/scripts/legacy/S10_execute_translation_deepl.py
pipeline/scripts/legacy/07b_execute_menu_v3_guardian.py
```

These should remain retired from production use unless formalized.

No active core title script was found using `latin`, `cp1252`, or non-UTF-8 decoding for title metadata.

## Temporary and legacy script audit

No actual `*Copia*` / `*Cópia*` duplicate files were found in the current `pipeline/scripts` tree, but legacy docs still reference historical duplicate files and retirement work.

Scripts that should be retired, fenced, or formalized before the next translation batch:

```text
pipeline/scripts/legacy/05_translate_pilot_v5_surgeon.py
pipeline/scripts/legacy/05a_upload_glossary_deepl.py
pipeline/scripts/legacy/07b_execute_menu_v3_guardian.py
pipeline/scripts/legacy/14_sync_titles_from_ledger.py
pipeline/scripts/legacy/S10_execute_translation_deepl.py
pipeline/scripts/tools/run_sp11_and_report.sh
pipeline/scripts/core/SP13_remediate_buda.py
```

Notes:

- `legacy/14_sync_titles_from_ledger.py` resets `titles.pt` to `None` when syncing EN titles from the ledger. It uses an old absolute `BASE_DIR` and should stay retired.
- `legacy/S10_execute_translation_deepl.py` appears superseded by core `SP10_translate_deepl.py`.
- `legacy/05_translate_pilot_v5_surgeon.py` and `legacy/05a_upload_glossary_deepl.py` are old DeepL/glossary paths.
- `tools/run_sp11_and_report.sh` is useful conceptually, but it hardcodes `/beng-fut/pipeline/scripts` and `/beng-fut/pipeline/09-csl`; it is not safe to run as-is in this workspace.
- `core/SP13_remediate_buda.py` is explicitly an emergency one-shot remediation script. It should be documented as retired after its intended remediation, or converted into a dry-run-only audit utility.

## Title contamination scan

The exact requested CSL metadata scan failed due `titles.pt: null` values, as noted above.

The null-safe rerun checked all identity metadata currently present on disk:

```text
checked=748
null_pt=439
hits=0
```

This supports the #FlagFix_028 conclusion: no current corpus-wide `titles.pt` Italian-marker contamination was found after the local `LD.AA.000` metadata correction.

## Recommended next action

Before the next translation/title batch:

1. Do not run `SP11 --apply` unattended.
2. Add or require a title QA gate for `titles.pt` after DeepL output and before accepting metadata writes.
3. Make the Italian-marker title audit null-safe and save it as a small reusable tool or documented command.
4. Fence retired legacy scripts so operators do not accidentally use old DeepL/title paths.
5. Replace or update `tools/run_sp11_and_report.sh` hardcoded `/beng-fut` paths before considering it operational.
6. Add #FlagFix_028 style contamination markers to the post-title audit list:

```text
 il 
 lo 
 gli 
 della 
 del 
 delle 
 degli 
 nell
 sull
 alla 
 al 
```

## Explicit no-change confirmation

No build was run.
No pipeline was run.
No deploy was run.
No translation was run.
No Netlify/Vitrine update was made.
No Cloudflare configuration was touched.
`/home/sanghop/axis/axis-niddhi-published` was not touched.

Only this report file was created for #FlagFix_029.
