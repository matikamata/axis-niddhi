# FLAGFIX_032 - Dry-run preflight for next translation batch

Date: 2026-05-18
Workspace: `/home/sanghop/axis/axis-niddhi-production`
Mode: audit/report only
Checkpoint reference: `checkpoint/flagfix-028-031-title-pipeline-safety-20260518`

## Repository state

Commands run:

```bash
git status -sb
git log --oneline --decorate -n 12
git tag --list "checkpoint/flagfix-028-031*" | sort
```

Observed:

```text
## flagfix-032-translation-batch-preflight
```

Checkpoint found:

```text
checkpoint/flagfix-028-031-title-pipeline-safety-20260518
```

Current HEAD:

```text
46d7f5b2 (HEAD -> flagfix-032-translation-batch-preflight, tag: checkpoint/flagfix-028-031-title-pipeline-safety-20260518, origin/main, origin/HEAD, main) Merge pull request #124 from matikamata/flagfix-031-fence-retired-translation-scripts
```

## Title QA gate

Command run:

```bash
python3 pipeline/scripts/tools/audit_pt_titles_language_contamination.py
echo "exit_code=$?"
```

Observed:

```text
checked=748
null_pt_titles=439
hits=0
exit_code=0
```

Result: PASS. No suspicious Italian-marker `titles.pt` hits were found in current CSL identity metadata.

## Retired script fence confirmation

Command run:

```bash
grep -RIn \
  "AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT\|AXIS_ALLOW_HARDCODED_LEGACY_TOOL\|AXIS_ALLOW_EMERGENCY_REMEDIATION" \
  pipeline/scripts/legacy pipeline/scripts/tools pipeline/scripts/core/SP13_remediate_buda.py
```

Confirmed fences:

```text
AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT
  pipeline/scripts/legacy/05a_upload_glossary_deepl.py
  pipeline/scripts/legacy/05_translate_pilot_v5_surgeon.py
  pipeline/scripts/legacy/14_sync_titles_from_ledger.py
  pipeline/scripts/legacy/S10_execute_translation_deepl.py
  pipeline/scripts/legacy/07b_execute_menu_v3_guardian.py

AXIS_ALLOW_HARDCODED_LEGACY_TOOL
  pipeline/scripts/tools/run_sp11_and_report.sh

AXIS_ALLOW_EMERGENCY_REMEDIATION
  pipeline/scripts/core/SP13_remediate_buda.py
```

Result: PASS. #FlagFix_031 fences are present.

## PT title completeness

Read-only CSL metadata audit:

```text
total_identity_files=748
json_errors=0
titles_pt_null=439
titles_pt_empty=0
titles_pt_present=309
```

`pt_source` distribution:

```text
null: 439
deepl_v5: 216
deepl_v5_sp11: 91
deepL_v5: 1
manual_override: 1
```

Notes:

- The 439 null PT titles are expected pending title/body translation work, not a crash condition.
- The mixed-case `deepL_v5` singleton is harmless for preflight but worth normalizing in a later metadata hygiene sprint if desired.

## Translation Control Center

Files found:

```text
pipeline/metadata/Print_Translation_Control_Center.csv
pipeline/metadata/Translation_Control_Center.csv
```

### Translation_Control_Center.csv

```text
rows_total=748
columns=Fin-dex, PD#PN, Section, Slug, Status, Chars, Est_Cost_USD, Quota_Impact_%, COMMAND
Status:
  DONE: 309
  PENDING: 439
COMMAND:
  <blank>: 748
likely_next_batch_candidates=0
pending_with_existing_pt_content=0
done_without_pt_content=0
pending_with_existing_pt_title=0
```

Assessment: coherent with CSL. No next translation batch is selected yet because `COMMAND` is blank for all rows.

### Print_Translation_Control_Center.csv

```text
rows_total=748
columns=Fin-dex, PD#PN, Section, Slug, Status, Chars, Est_Cost_USD, Quota_Impact_%, COMMAND, Printed?, Prin-dex, Lote
Status:
  DONE: 153
  PENDING: 595
COMMAND:
  <blank>: 688
  YES: 60
likely_next_batch_candidates=59
pending_with_existing_pt_content=156
done_without_pt_content=0
pending_with_existing_pt_title=156
```

Assessment: this file appears stale or print-specific relative to current CSL translation state. It should not be used as the SP10 translation batch selector without refresh/reconciliation.

## LD.AA.000 static artifact staleness

Command run:

```bash
grep -RIn "Vivendo il Dhamma\|Vivendo o Dhamma" pipeline/13-static-site pipeline/13-ssg 2>/dev/null | head -100
```

Observed stale generated artifacts:

```text
pipeline/13-static-site/index.json:4011:          "title_pt": "Vivendo il Dhamma",
pipeline/13-static-site/search_index.json:4762:    "title_pt": "Vivendo il Dhamma",
pipeline/13-static-site/pages/LD.AA.006/index.html:271:        <span class="pathway-title title-pt">Vivendo il Dhamma</span>
pipeline/13-static-site/pages/LD.AA.000/index.html:88:    <h1 class="title-pt">Vivendo il Dhamma</h1>
pipeline/13-static-site/pages/LD.BB.001/index.html:222:        <span class="pathway-title title-pt">Vivendo il Dhamma</span>
pipeline/13-static-site/archive.html:11531:        Vivendo il Dhamma
```

Also observed legitimate/newer body references to:

```text
Vivendo o Dhamma
```

Conclusion: CSL metadata has been corrected by #FlagFix_028, but static output remains stale. This is expected because no static regeneration/promotion has been run in the safety batch.

## Recommendation

Ready for translation batch apply: not yet.

Reasons:

1. `Translation_Control_Center.csv` has no selected rows (`COMMAND` blank for all 748 rows).
2. `Print_Translation_Control_Center.csv` has `YES` rows but is stale/print-specific and contradicts current CSL for 156 rows with existing PT content/title.
3. Static artifacts still contain stale `Vivendo il Dhamma`, but static regeneration should be handled as a separate batch promotion step, not inside this preflight.

Recommended next action:

1. Keep static regeneration/promotion for later batch closure, not now.
2. Choose the next translation batch only in `pipeline/metadata/Translation_Control_Center.csv`, not the print control center.
3. Before any SP10/SP11 apply, rerun:

```bash
python3 pipeline/scripts/tools/audit_pt_titles_language_contamination.py
```

4. After any title-writing batch and before static generation, rerun the same QA gate and reconcile any hits.
5. Reconcile or regenerate `Print_Translation_Control_Center.csv` before relying on its `Status`/`COMMAND` fields for print workflow.

## Explicit no-change confirmation

No DeepL call was made.
No translation was run.
No CSL content was modified.
No Translation Control Center file was modified.
No build was run.
No pipeline was run.
No deploy was run.
No Netlify/Vitrine update was made.
No Cloudflare configuration was touched.
`/home/sanghop/axis/axis-niddhi-published` was not touched.

Only this #FlagFix_032 report was created.
