# FlagFix 076 - LABZ Flower Candidate Compression

Date: 2026-05-19

## Context

Latest checkpoint:

- `checkpoint/flagfix-075-labz-candidate-image-review-20260519`

#FlagFix_075 approved two LABZ flower candidates for MVP planning and deferred the bee candidates for revision. This sprint compressed only the two approved flower candidates outside the repository.

No site integration occurred.

## Directories

Source directory:

- `/home/sanghop/axis/labz-ambient-candidates/flagfix_074_candidates/`

Output directory:

- `/home/sanghop/axis/labz-ambient-candidates/flagfix_076_compressed_flowers/`

## Source Files

Approved source PNG candidates:

- `labz-ora-pro-nobis-left-candidate-01.png`
- `labz-lily-right-candidate-01.png`

Source file checks:

```text
EXISTS labz-ora-pro-nobis-left-candidate-01.png
EXISTS labz-lily-right-candidate-01.png
```

Source SHA256:

```text
5bd16b5f5e8f28c0b13546ef075714fe556d7b6be706f3a97cced15709bbcce6  labz-ora-pro-nobis-left-candidate-01.png
6a99805a1783e1062d7e2b053806a52d829e05384b6fd52e09ba7e489705618b  labz-lily-right-candidate-01.png
```

## Compressed Files

Compressed WebP outputs:

- `labz-ora-pro-nobis-left-mvp-01.webp`
- `labz-lily-right-mvp-01.webp`

Compression tool:

- Python/Pillow WebP support.

Compression settings:

- WebP quality: `82`
- WebP method: `6`
- Alpha preserved.
- Dimensions preserved.

## Technical Comparison

| Source PNG | Source bytes | WebP | WebP bytes | Dimensions | Mode | Transparency | Ratio |
|---|---:|---|---:|---|---|---|---:|
| `labz-ora-pro-nobis-left-candidate-01.png` | `556091` | `labz-ora-pro-nobis-left-mvp-01.webp` | `89046` | `1536x1536` | `RGBA` | yes | `0.160` |
| `labz-lily-right-candidate-01.png` | `619121` | `labz-lily-right-mvp-01.webp` | `85962` | `1536x1536` | `RGBA` | yes | `0.139` |

Pillow readback confirmed:

```text
labz-lily-right-mvp-01.webp (1536, 1536) RGBA alpha=True 85962
labz-ora-pro-nobis-left-mvp-01.webp (1536, 1536) RGBA alpha=True 89046
```

External comparison CSV:

- `/home/sanghop/axis/labz-ambient-candidates/flagfix_076_compressed_flowers/technical_comparison.csv`

## SHA256 Summary

```text
a0a4421e01429c23faa9d66574002148be7ad120a7e2bbfc211845a423495e00  labz-flower-compression-contact-sheet-flagfix-076.png
4e0d1c419bfabcb9a69309622a7378d20a583e01a4f1e8b0d3b45a92e6206bb0  labz-lily-right-mvp-01.webp
590ad14895dc5a394683d6f4b2a5bea174d50e5851a77a7e949038e87e4f1016  labz-ora-pro-nobis-left-mvp-01.webp
2d495228bba7d484ff75aeae5e5d608c27d3aa70785a8b472cef365f10f372b5  technical_comparison.csv
```

Full external hash file:

- `/home/sanghop/axis/labz-ambient-candidates/flagfix_076_compressed_flowers/sha256sums.txt`

## Contact Sheet

Before/after contact sheet:

- `/home/sanghop/axis/labz-ambient-candidates/flagfix_076_compressed_flowers/labz-flower-compression-contact-sheet-flagfix-076.png`

Contact sheet details:

- `810x982`
- RGB PNG
- Shows Ora-pro-nobis PNG vs WebP and lily PNG vs WebP.

Visual note:

- The compressed WebP candidates remain visually close to the source candidates in the contact sheet.
- Human review is still required before integration.

## Compression Target

Target:

- Ideally under `200-350 KB` per decorative image.

Result:

- Ora-pro-nobis WebP: `89046` bytes, target met.
- Lily WebP: `85962` bytes, target met.

Recommendation status:

- `READY FOR HUMAN VISUAL REVIEW`
- Not ready for site integration yet.

## Proposed Next Sprint

`#FlagFix_077 - Human review compressed LABZ flower assets`

Suggested scope:

- inspect the compressed WebP files and before/after contact sheet;
- decide whether both compressed flower assets are acceptable;
- if approved, plan repo asset integration in a later sprint;
- do not integrate into the site in #077 unless explicitly approved.

## Explicit Non-Actions

- No images were moved into the repo.
- No images were committed to the repo.
- No repo asset directories were created.
- No bee images were modified.
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
