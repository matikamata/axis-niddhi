# FlagFix 039 - Surgical EN Title Metadata Correction Batch 1

Date: 2026-05-18

## Scope

This sprint corrected five high-confidence EN title metadata corruptions identified by #FlagFix_038.

Only `titles.en` was corrected in CSL `identity.json` files. No PT title/content, static artifact, metadata CSV, script, renderer, build, pipeline, deploy, or Vitrine change was made.

## Corrections

| PD#PN | Old title | New title | Status | Evidence |
|---|---|---|---|---|
| BA.AA.001 | `Pali Suttas In Tipie1B9Adaka Direct Translations Are Wrong` | `Pāli Suttās in Tipiṭaka – Direct Translations are Wrong` | corrected | `PDPN_01_Operational.csv` line 751; EN body line 1 contains `Pāli`, `suttās`, and `Tipiṭaka` |
| BA.AA.005 | `Arammae1B987A Sensory Input Initiates Critical Processes` | `Ārammaṇa (Sensory Input) Initiates Critical Processes` | corrected | `PDPN_01_Operational.csv` line 754; EN body line 1 contains `Ārammaṇa` and sensory input |
| BM.CC.006 | `Tae1B987Ha Result Of Sanna Giving Rise To Mind Made Vedana` | `Taṇhā – Result of Saññā Giving Rise to Mind-Made Vedanā` | corrected | `PDPN_01_Operational.csv` line 626; EN body line 1 contains `Taṇhā`, `vedanā`, and `saññā` |
| DS.DD.005 | `Sandie1B9Ade1B9Adhiko What Does It Mean` | `Sandiṭṭhiko – What Does It Mean?` | corrected | `PDPN_01_Operational.csv` line 274; EN body line 1 contains `Sandiṭṭhiko` |
| IS.BB.004 | `Aniccae1B981 Viparie1B987Ami Annathabhavi A Critical Verse` | `Aniccaṁ Vipariṇāmi Aññathābhāvi – A Critical Verse` | corrected | `PDPN_01_Operational.csv` line 580; EN body lines 1 and 41 contain `Aniccaṁ Vipariṇāmi Aññathābhāvi` |

## Files Changed On Disk

- `pipeline/09-csl/BA.AA.001/meta/identity.json`
- `pipeline/09-csl/BA.AA.005/meta/identity.json`
- `pipeline/09-csl/BM.CC.006/meta/identity.json`
- `pipeline/09-csl/DS.DD.005/meta/identity.json`
- `pipeline/09-csl/IS.BB.004/meta/identity.json`

Review CSV:

- `review/title-corruption/flagfix_039_en_title_correction_batch_1.csv`

Note: `pipeline/09-csl` changes do not appear in normal `git status` output in this workspace. The tracked diff for this sprint records the report and review CSV; the CSL metadata corrections were confirmed by re-reading each JSON file.

## Post-Audit Result

Suspicious title audit after this batch:

- checked: 748 identity files
- hits: 18

The count dropped from 23 to 18, matching the five corrected EN titles.

Remaining hits:

- `CH.AA.005` EN
- `DS.DD.003` EN
- `DS.DD.007` EN
- `ER.FF.004` EN
- `KD.DD.005` EN and PT
- `KD.II.010` EN and PT
- `KD.JJ.010` EN and PT
- `KD.JJ.011` EN
- `PS.DD.004` EN
- `PS.GG.004` EN
- `PS.II.011` EN
- `TL.II.008` EN and PT
- `TL.II.013` EN and PT

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
