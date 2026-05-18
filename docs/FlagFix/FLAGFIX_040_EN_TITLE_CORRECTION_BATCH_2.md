# FlagFix 040 - Surgical EN Title Metadata Correction Batch 2

Date: 2026-05-18

Checkpoint reference:

- `checkpoint/flagfix-039-en-title-correction-batch-1-20260518`

## Scope

This sprint corrected five high-confidence EN title metadata corruptions remaining after #FlagFix_039.

Only `titles.en` was corrected in CSL `identity.json` files. No PT title/content, static artifact, metadata CSV, script, renderer, build, pipeline, deploy, or Vitrine change was made.

## Corrections

| PD#PN | Old title | New title | Status | Evidence |
|---|---|---|---|---|
| CH.AA.005 | `Rupa Dhamma Appae1B9Adigha Rupa And Namagotta Memories` | `Rupa, Dhammā (Appaṭigha Rupa) and Nāmagotta (Memories)` | corrected | `PDPN_01_Operational.csv` line 758; EN body lines 3-4 contain `Appaṭigha Rupa` and `Nāmagotta` |
| DS.DD.003 | `Mind Pleasing Things In The World Arise Via Pae1B9Adicca Samuppada` | `“Mind-Pleasing Things” in the World Arise via Paṭicca Samuppāda` | corrected | `PDPN_01_Operational.csv` line 272 gives exact title and encoded URL slug |
| DS.DD.007 | `Kama Sanna How To Bypass To Cultivate Satipae1B9Ade1B9Adhana` | `Kāma Saññā – How to Bypass to Cultivate Satipaṭṭhāna` | corrected | `PDPN_01_Operational.csv` line 276; EN body line 1 contains `Kāma saññā` and `Satipaṭṭhāna` |
| ER.FF.004 | `Anapanasati Not About Breath Icchanae1B985Gala Sutta` | `Ānāpānasati Not About Breath – Icchā­naṅga­la Sutta` | corrected | `PDPN_01_Operational.csv` line 359; EN body lines 56 and 63 contain `Ānāpānasati` and `Satipaṭṭhāna` |
| KD.DD.005 | `Kamma Are Done With Abhisae1B985Khara Types Of Abhisae1B985Khara` | `Kamma are Done with Abhisaṅkhāra – Types of Abhisaṅkhāra` | corrected | `PDPN_01_Operational.csv` line 87; EN body lines 32, 52, 61, and 89 contain `Abhisaṅkhāra` |

No candidates were deferred.

## Files Changed On Disk

- `pipeline/09-csl/CH.AA.005/meta/identity.json`
- `pipeline/09-csl/DS.DD.003/meta/identity.json`
- `pipeline/09-csl/DS.DD.007/meta/identity.json`
- `pipeline/09-csl/ER.FF.004/meta/identity.json`
- `pipeline/09-csl/KD.DD.005/meta/identity.json`

Review CSV:

- `review/title-corruption/flagfix_040_en_title_correction_batch_2.csv`

Note: `pipeline/09-csl` changes do not appear in normal `git status` output in this workspace. The CSL metadata corrections were confirmed by re-reading each JSON file.

## Post-Audit Result

Suspicious title audit after this batch:

- checked: 748 identity files
- hits: 13

The count dropped from 18 to 13, matching the five corrected EN titles.

Remaining hits include PT title fields for some records. Those were intentionally not touched in this sprint.

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
- Did not mass-correct beyond the five approved candidates.
