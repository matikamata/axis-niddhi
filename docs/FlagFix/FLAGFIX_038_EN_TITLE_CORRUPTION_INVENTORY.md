# FlagFix 038 - Corpus-Wide EN Title Corruption Inventory

Date: 2026-05-18

## Scope

This sprint created a read-only inventory of suspicious ASCII/hex artifacts in CSL title metadata after the #FlagFix_037 correction for `BA.AA.004`.

No title corrections were made in this sprint.

## Inputs Checked

- `pipeline/09-csl/*/meta/identity.json`
- `pipeline/09-csl/*/source/en-US/content.html`
- `pipeline/13-static-site/pages/*/index.html`
- `pipeline/13-static-site/archive.html`
- `pipeline/13-static-site/index.json`
- `pipeline/13-static-site/search_index.json`
- `pipeline/metadata/Translation_Control_Center.csv`
- `pipeline/metadata/PDPN_01_Operational.csv`
- `pipeline/metadata/slug_map.json`

Patterns checked:

- `e1B`
- `B987`
- `[A-Za-z]\d[A-Fa-f0-9]{3,}[A-Za-z]`

## Summary

- identity files checked: 748
- suspicious title hits: 23
- `BA.AA.004` present in this inventory: no
- high-confidence candidates: 23

All remaining hits have EN body evidence containing likely Unicode/Pāli forms. Most EN title hits also appear in `Translation_Control_Center.csv` and `slug_map.json`, and all checked static artifacts currently contain the same stale corrupted title strings.

## Inventory

CSV inventory:

- `review/title-corruption/flagfix_038_en_title_corruption_inventory.csv`

| PD#PN | Field | Current title | Metadata also affected | Confidence |
|---|---|---|---|---|
| BA.AA.001 | en | Pali Suttas In Tipie1B9Adaka Direct Translations Are Wrong | TCC; slug_map | high |
| BA.AA.005 | en | Arammae1B987A Sensory Input Initiates Critical Processes | TCC; slug_map | high |
| BM.CC.006 | en | Tae1B987Ha Result Of Sanna Giving Rise To Mind Made Vedana | TCC; slug_map | high |
| CH.AA.005 | en | Rupa Dhamma Appae1B9Adigha Rupa And Namagotta Memories | TCC; slug_map | high |
| DS.DD.003 | en | Mind Pleasing Things In The World Arise Via Pae1B9Adicca Samuppada | TCC; slug_map | high |
| DS.DD.005 | en | Sandie1B9Ade1B9Adhiko What Does It Mean | TCC; slug_map | high |
| DS.DD.007 | en | Kama Sanna How To Bypass To Cultivate Satipae1B9Ade1B9Adhana | TCC; slug_map | high |
| ER.FF.004 | en | Anapanasati Not About Breath Icchanae1B985Gala Sutta | TCC; slug_map | high |
| IS.BB.004 | en | Aniccae1B981 Viparie1B987Ami Annathabhavi A Critical Verse | TCC; slug_map | high |
| KD.DD.005 | en | Kamma Are Done With Abhisae1B985Khara Types Of Abhisae1B985Khara | TCC; slug_map | high |
| KD.DD.005 | pt | Kamma já terminou o Abhisae1B985Khara Tipos de Abhisae1B985Khara | not found by exact title/slug search | high |
| KD.II.010 | en | Sensory Experience Pae1B9Adicca Samuppada And Pancupadanakkhandha | TCC; slug_map | high |
| KD.II.010 | pt | Experiência sensorial Pae1B9Adicca Samuppada e Pancupadanakkhandha | not found by exact title/slug search | high |
| KD.JJ.010 | en | Namarupa In Vipaka Vinnae1B987A | TCC; slug_map | high |
| KD.JJ.010 | pt | Namarupa em Vipaka Vinnae 1B987A | not found by exact title/slug search | high |
| KD.JJ.011 | en | Namarupa In Pae1B9Adicca Samuppada | TCC; slug_map | high |
| PS.DD.004 | en | Difference Between Dhamma And Sae1B985Khara | TCC; slug_map | high |
| PS.GG.004 | en | Sae1B985Khara An Introduction | TCC; slug_map | high |
| PS.II.011 | en | Namarupa Vinnae1B987A Dhamma Closely Related | TCC; slug_map | high |
| TL.II.008 | en | Fooled By Distorted Sanna Sanjanati Origin Of Attachment Tae1B987Ha | TCC; slug_map | high |
| TL.II.008 | pt | Enganado por Sanna Sanjanati Distorcido Origem do Vínculo Tae1B987Ha | not found by exact title/slug search | high |
| TL.II.013 | en | Sanna Nidana Hi Papanca Sae1B985Kha Immoral Thoughts Based On Distorted Sanna | TCC; slug_map | high |
| TL.II.013 | pt | Sanna Nidana Hi Papanca Sae1B985Kha Pensamentos imorais baseados em Sanna distorcido | not found by exact title/slug search | high |

## Interpretation

The remaining title corruption appears to be a legacy metadata/title extraction or migration issue, not a renderer issue and not a DeepL issue.

The static site is stale relative to any future metadata fixes because no static regeneration was run. For current hits, static artifacts mirror the corrupted metadata.

Five hits are in `titles.pt`, but they are paired with the same corrupted EN metadata family. These PT titles should be reviewed only after the corresponding EN title is corrected and the intended source form is confirmed.

## Recommendation For FlagFix 039

Create a surgical correction sprint for a small batch of high-confidence EN titles. Recommended first candidates:

- `BA.AA.001`
- `BA.AA.005`
- `BM.CC.006`
- `DS.DD.005`
- `IS.BB.004`

For each candidate, confirm the intended title from source body and/or original operational metadata before editing `identity.json`.

Do not mass-correct by automated substitution alone. Several title strings contain multiple Pāli terms, and the correct title casing/spelling may need per-title evidence.

## No-Change Confirmations

- Did not touch `/home/sanghop/axis/axis-niddhi-published`.
- Did not update Netlify/Vitrine.
- Did not run build, pipeline, or deploy.
- Did not call DeepL.
- Did not translate anything.
- Did not modify CSL content.
- Did not modify metadata CSVs.
- Did not modify `Translation_Control_Center.csv`.
- Did not modify SP10/SP11 behavior.
- Did not correct any titles in this sprint.
