# FlagFix 041 - Surgical EN Title Metadata Correction Batch 3

Date: 2026-05-18

Checkpoint reference:

- `checkpoint/flagfix-040-en-title-correction-batch-2-20260518`

## Scope

This sprint corrected five high-confidence EN title metadata corruptions remaining after #FlagFix_040.

Only `titles.en` was corrected in CSL `identity.json` files. No PT title/content, static artifact, metadata CSV, script, renderer, build, pipeline, deploy, or Vitrine change was made.

## Corrections

| PD#PN | Old title | New title | Status | Evidence |
|---|---|---|---|---|
| KD.II.010 | `Sensory Experience Pae1B9Adicca Samuppada And Pancupadanakkhandha` | `Sensory Experience, Paṭicca Samuppāda, and pañcupādānakkhandha` | corrected | `PDPN_01_Operational.csv` line 161; EN body line 77 contains `Paṭicca Samuppāda` |
| KD.JJ.010 | `Namarupa In Vipaka Vinnae1B987A` | `Nāmarupa in Vipāka Viññāṇa` | corrected | `PDPN_01_Operational.csv` line 180; EN body image filename references Namarupa context |
| KD.JJ.011 | `Namarupa In Pae1B9Adicca Samuppada` | `Nāmarupa in Idappaccayātā Paṭicca Samuppāda` | corrected | `PDPN_01_Operational.csv` line 181 gives exact title and encoded URL slug |
| PS.DD.004 | `Difference Between Dhamma And Sae1B985Khara` | `Difference Between Dhammā and Saṅkhāra` | corrected | `PDPN_01_Operational.csv` line 86; EN body lines 72-73 contain `Saṅkhāra`/`Sankhārā` discussion |
| PS.GG.004 | `Sae1B985Khara An Introduction` | `Saṅkhāra – An Introduction` | corrected | `PDPN_01_Operational.csv` line 530; EN body line 43 references `Saṅkhāra` resources |

No candidates were deferred.

## Files Changed On Disk

- `pipeline/09-csl/KD.II.010/meta/identity.json`
- `pipeline/09-csl/KD.JJ.010/meta/identity.json`
- `pipeline/09-csl/KD.JJ.011/meta/identity.json`
- `pipeline/09-csl/PS.DD.004/meta/identity.json`
- `pipeline/09-csl/PS.GG.004/meta/identity.json`

Review CSV:

- `review/title-corruption/flagfix_041_en_title_correction_batch_3.csv`

Note: `pipeline/09-csl` changes do not appear in normal `git status` output in this workspace. The CSL metadata corrections were confirmed by re-reading each JSON file.

## Post-Audit Result

Suspicious title audit after this batch:

- checked: 748 identity files
- hits: 8

The count dropped from 13 to 8, matching the five corrected EN titles.

Remaining hits:

- `PS.II.011` EN
- `TL.II.008` EN
- `TL.II.013` EN
- five PT title fields intentionally left untouched

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
