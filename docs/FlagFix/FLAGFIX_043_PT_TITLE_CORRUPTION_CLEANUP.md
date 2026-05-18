# FlagFix 043 - PT Title Corruption Cleanup After EN Stabilization

Date: 2026-05-18

Checkpoint reference:

- `checkpoint/flagfix-042-final-en-title-correction-20260518`

## Scope

This sprint corrected the remaining corrupted `titles.pt` metadata values after the EN title cleanup from #FlagFix_037 through #FlagFix_042.

Only `titles.pt` was corrected in CSL `identity.json` files. PT body content and EN titles were not changed.

## Pre-Audit

Suspicious title audit before this batch:

- checked: 748 identity files
- total hits: 5
- EN hits: 0
- PT hits: 5

PT candidates:

- `KD.DD.005`
- `KD.II.010`
- `KD.JJ.010`
- `TL.II.008`
- `TL.II.013`

## Corrections

| PD#PN | Old PT title | New PT title | Status | Evidence |
|---|---|---|---|---|
| KD.DD.005 | `Kamma já terminou o Abhisae1B985Khara Tipos de Abhisae1B985Khara` | `Kamma é feito com Abhisaṅkhāra – Tipos de Abhisaṅkhāra` | corrected | stabilized EN title; PT body contains `Abhisaṅkhāra` repeatedly |
| KD.II.010 | `Experiência sensorial Pae1B9Adicca Samuppada e Pancupadanakkhandha` | `Experiência sensorial, Paṭicca Samuppāda e Pañcupādānakkhandha` | corrected | stabilized EN title; PT body line 9 contains `Paṭicca Samuppāda` and `pañcupādānakkhandha` |
| KD.JJ.010 | `Namarupa em Vipaka Vinnae 1B987A` | `Nāmarupa em Vipāka Viññāṇa` | corrected | stabilized EN title; PT body opening paragraph contains `Nāmarupa` and `Vipāka Viññāṇa` |
| TL.II.008 | `Enganado por Sanna Sanjanati Distorcido Origem do Vínculo Tae1B987Ha` | `Enganado pela Saññā Distorcida (Sañjānāti) – Origem do Apego (Taṇhā)` | corrected | stabilized EN title; PT body opening paragraph contains `Saññā distorcida` and `Taṇhā`; related PT link text uses `Origem do apego` |
| TL.II.013 | `Sanna Nidana Hi Papanca Sae1B985Kha Pensamentos imorais baseados em Sanna distorcido` | `Saññā Nidānā hi Papañca Saṅkhā – Pensamentos imorais baseados em “Saññā Distorcida”` | corrected | stabilized EN title; PT body opening paragraph contains `Saññānidānā hi papañcasaṅkhā` and `Saññā distorcida` |

No PT cases were deferred.

## Files Changed On Disk

- `pipeline/09-csl/KD.DD.005/meta/identity.json`
- `pipeline/09-csl/KD.II.010/meta/identity.json`
- `pipeline/09-csl/KD.JJ.010/meta/identity.json`
- `pipeline/09-csl/TL.II.008/meta/identity.json`
- `pipeline/09-csl/TL.II.013/meta/identity.json`

Review CSV:

- `review/title-corruption/flagfix_043_pt_title_corruption_cleanup.csv`

Note: `pipeline/09-csl` changes do not appear in normal `git status` output in this workspace. The CSL metadata corrections were confirmed by re-reading each JSON file.

## Final Audit Result

Suspicious title audit after this batch:

- checked: 748 identity files
- total hits: 0
- EN hits: 0
- PT hits: 0

This closes the known ASCII/hex-like title metadata corruption inventory from #FlagFix_038.

## Static Staleness

Static artifacts were not touched and remain stale until an approved future regeneration/promotion batch.

Known stale areas include generated page HTML, archive, index JSON, and search index for corrected posts across #FlagFix_037 through #FlagFix_043.

## No-Change Confirmations

- Did not touch `/home/sanghop/axis/axis-niddhi-published`.
- Did not update Netlify/Vitrine.
- Did not run build, pipeline, or deploy.
- Did not call DeepL.
- Did not translate with external services.
- Did not modify PT body content.
- Did not modify EN titles.
- Did not modify metadata CSVs.
- Did not modify `Translation_Control_Center.csv`.
- Did not modify SP10/SP11 behavior.
- Did not touch static artifacts.
- Corrected only the remaining corrupted `titles.pt` fields.
