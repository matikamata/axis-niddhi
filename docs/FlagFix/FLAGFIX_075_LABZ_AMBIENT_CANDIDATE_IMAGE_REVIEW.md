# FlagFix 075 - LABZ Ambient Candidate Image Review

Date: 2026-05-19

## Context

Latest checkpoint:

- `checkpoint/flagfix-074-labz-ambient-candidate-images-20260519`

#FlagFix_074 generated first-pass LABZ ambient candidate images outside the repository. This sprint reviews those external candidates and records technical metadata plus visual decisions.

No site integration occurred.

## Candidate Directory

External candidate directory:

- `/home/sanghop/axis/labz-ambient-candidates/flagfix_074_candidates/`

Inventory:

- `file_inventory.txt`
- `labz-ambient-candidates-contact-sheet-flagfix-074.png`
- `labz-bee-amber-green-soft-candidate-01.png`
- `labz-bee-blue-soft-candidate-01.png`
- `labz-bee-gold-soft-candidate-01.png`
- `labz-lily-right-candidate-01.png`
- `labz-ora-pro-nobis-left-candidate-01.png`
- `ls_lh.txt`
- `sha256sums.txt`

Directory size:

- `2.2M`

## Technical Summary Table

| Filename | Dimensions | Mode | Transparency | Size bytes | SHA256 short |
|---|---:|---|---|---:|---|
| `labz-ambient-candidates-contact-sheet-flagfix-074.png` | `1192x912` | `RGB` | no | `134964` | `76ca9f40` |
| `labz-bee-amber-green-soft-candidate-01.png` | `1536x1536` | `RGBA` | yes | `301692` | `fe582f48` |
| `labz-bee-blue-soft-candidate-01.png` | `1536x1536` | `RGBA` | yes | `302779` | `1ee8b547` |
| `labz-bee-gold-soft-candidate-01.png` | `1536x1536` | `RGBA` | yes | `303237` | `5bb13bae` |
| `labz-lily-right-candidate-01.png` | `1536x1536` | `RGBA` | yes | `619121` | `6a99805a` |
| `labz-ora-pro-nobis-left-candidate-01.png` | `1536x1536` | `RGBA` | yes | `556091` | `5bd16b5` |

Technical notes:

- All five candidate images have RGBA transparency.
- The contact sheet is RGB and is review-only.
- Flora files are above the preferred final size target and need compression or simplification before integration.
- Bee files are smaller than flora but still should be compressed if a revised bee direction is later approved.

## Review Decision Table

| Candidate | Decision | Reason |
|---|---|---|
| `labz-ora-pro-nobis-left-candidate-01.png` | `APPROVE FOR MVP PLANNING` | The left-side floral/vine composition is soft, quiet, side-margin friendly, and visually subordinate. It should move forward only after compression/fit testing. |
| `labz-lily-right-candidate-01.png` | `APPROVE FOR MVP PLANNING` | The lily composition is calm and suitable for a right-side ambient layer. It is larger than ideal and needs optimization, but the tone is aligned. |
| `labz-bee-gold-soft-candidate-01.png` | `REVISE` | Technically clean and transparent, but visually reads as a mascot/icon. It risks being too cute and too attention-drawing near Dhamma text. |
| `labz-bee-blue-soft-candidate-01.png` | `REVISE` | Same issue as the gold bee: clear and soft, but too character-like for the desired noble ambient side layer. |
| `labz-bee-amber-green-soft-candidate-01.png` | `REVISE` | Palette is more subdued, but the form still reads as a cute icon/mascot. Needs a less anthropomorphic, more naturalistic or silhouette-like approach. |

Visual inspection basis:

- Contact sheet reviewed locally.
- Candidate review is sufficient for first-pass direction decisions, but final integration still requires human visual review in the actual LABZ page context.

## Criteria Review

Criteria applied:

- calm / contemplative;
- noble / not childish;
- low distraction;
- suitable for page side margins;
- transparent background;
- no text;
- no symbols implying claims;
- no medical, therapeutic, cognitive, subliminal, healing, wellness, or performance implication;
- not visually competing with Dhamma content;
- suitable for future WebP compression.

Findings:

- Flora candidates pass tone and placement criteria but need compression and layout preview.
- Bee candidates pass transparency and no-text criteria but do not yet pass tone/seriousness criteria.
- No candidate contains text or claim-implying symbols.

## Suggested MVP Set

Suggested MVP set for the next technical pass:

- `labz-ora-pro-nobis-left-candidate-01.png`
- `labz-lily-right-candidate-01.png`

Do not include the current bee candidates in the MVP integration set. Bees should be revised before use.

Suggested future bee direction:

- less anthropomorphic;
- smaller;
- more naturalistic or silhouette-based;
- no large face-like eyes;
- reduced saturation;
- sparse use as optional accents only.

## Next Sprint Recommendation

Recommended next sprint:

- `#FlagFix_076 - Compress approved LABZ flora candidates outside repo`

Suggested #FlagFix_076 scope:

- compress only the two approved flora candidates outside repo;
- create WebP versions;
- record sizes, dimensions, and SHA256 values;
- optionally create a simple side-margin mock/contact sheet outside repo;
- do not integrate into the site yet.

Alternative if operator prefers a fuller candidate set first:

- `#FlagFix_076 - Generate revised LABZ bee candidate images`

## Explicit Non-Actions

- No images were moved into the repo.
- No images were committed to the repo.
- No repo asset directories were created.
- No CSS was modified.
- No HTML was modified.
- No JavaScript was modified.
- No generated static output was modified.
- No build or pipeline run.
- No deploy.
- No Netlify upload.
- No DeepL call.
- No translation.
- No CSL modification.
- No metadata CSV modification.
- No `Translation_Control_Center.csv` modification.
- No TCC/SP10/SP11 modification.
- No `axis-niddhi-published` modification.
