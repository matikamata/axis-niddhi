# FlagFix 042 - Surgical EN Title Metadata Correction Final Batch

Date: 2026-05-18

Checkpoint reference:

- `checkpoint/flagfix-041-en-title-correction-batch-3-20260518`

## Scope

This sprint corrected the final remaining suspicious EN title metadata hits from the #FlagFix_038 inventory.

Only `titles.en` was corrected in CSL `identity.json` files. PT title fields were intentionally not changed.

## Pre-Audit

Suspicious title audit before this batch:

- checked: 748 identity files
- total hits: 8
- EN hits: 3
- PT hits: 5

Remaining EN candidates:

- `PS.II.011`
- `TL.II.008`
- `TL.II.013`

## Corrections

| PD#PN | Old title | New title | Status | Evidence |
|---|---|---|---|---|
| PS.II.011 | `Namarupa Vinnae1B987A Dhamma Closely Related` | `Nāmarupa, Viññāṇa, Dhammā – Closely Related` | corrected | `PDPN_01_Operational.csv` line 562; EN body image filename references `Namarupa-Vinnaṇa-Dhamma` |
| TL.II.008 | `Fooled By Distorted Sanna Sanjanati Origin Of Attachment Tae1B987Ha` | `Fooled by Distorted Saññā (Sañjānāti) – Origin of Attachment (Taṇhā)` | corrected | `PDPN_01_Operational.csv` line 443 gives exact title and encoded URL slug |
| TL.II.013 | `Sanna Nidana Hi Papanca Sae1B985Kha Immoral Thoughts Based On Distorted Sanna` | `Saññā Nidānā hi Papañca Saṅkhā – Immoral Thoughts Based on “Distorted Saññā”` | corrected | `PDPN_01_Operational.csv` line 447 gives exact title and encoded URL slug |

No EN candidates were deferred.

## Files Changed On Disk

- `pipeline/09-csl/PS.II.011/meta/identity.json`
- `pipeline/09-csl/TL.II.008/meta/identity.json`
- `pipeline/09-csl/TL.II.013/meta/identity.json`

Review CSV:

- `review/title-corruption/flagfix_042_en_title_correction_final_batch.csv`

Note: `pipeline/09-csl` changes do not appear in normal `git status` output in this workspace. The CSL metadata corrections were confirmed by re-reading each JSON file.

## Post-Audit Result

Suspicious title audit after this batch:

- checked: 748 identity files
- total hits: 5
- EN hits: 0
- PT hits: 5

PT-deferred hits:

- `KD.DD.005` `titles.pt`
- `KD.II.010` `titles.pt`
- `KD.JJ.010` `titles.pt`
- `TL.II.008` `titles.pt`
- `TL.II.013` `titles.pt`

These PT fields should be handled in a separate PT-title cleanup sprint after EN source titles are stable.

## Static Staleness

Static artifacts were not touched and remain stale until an approved future regeneration/promotion batch.

Known stale areas include generated page HTML, archive, index JSON, and search index for the corrected posts.

## No-Change Confirmations

- Did not touch `/home/sanghop/axis/axis-niddhi-published`.
- Did not update Netlify/Vitrine.
- Did not run build, pipeline, or deploy.
- Did not call DeepL.
- Did not translate anything.
- Did not modify PT content or PT title fields.
- Did not modify metadata CSVs.
- Did not modify `Translation_Control_Center.csv`.
- Did not modify SP10/SP11 behavior.
- Did not touch static artifacts.
- Did not correct anything beyond the remaining EN title corruption cases.
