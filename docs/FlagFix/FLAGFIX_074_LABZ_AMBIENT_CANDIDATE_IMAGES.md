# FlagFix 074 - LABZ Ambient Candidate Images

Date: 2026-05-19

## Context

Latest checkpoint:

- `checkpoint/flagfix-073-labz-candidate-image-generation-plan-20260519`

#FlagFix_073 planned external candidate generation for LABZ ambient visuals. This sprint generated first-pass candidates outside all Git repositories and recorded their inventory for review.

These are candidates only. They were not integrated into the site.

## Candidate Directory

External candidate directory:

- `/home/sanghop/axis/labz-ambient-candidates/flagfix_074_candidates/`

This directory is outside:

- `/home/sanghop/axis/axis-niddhi-production`
- `/home/sanghop/axis/axis-niddhi-published`

## Generated Files

Candidate images:

- `labz-ora-pro-nobis-left-candidate-01.png`
- `labz-lily-right-candidate-01.png`
- `labz-bee-gold-soft-candidate-01.png`
- `labz-bee-blue-soft-candidate-01.png`
- `labz-bee-amber-green-soft-candidate-01.png`

Contact sheet:

- `labz-ambient-candidates-contact-sheet-flagfix-074.png`

External inventory files:

- `file_inventory.txt`
- `sha256sums.txt`
- `ls_lh.txt`

## Dimensions And File Types

```text
labz-ambient-candidates-contact-sheet-flagfix-074.png | 1192x912  | RGB  | 134964 bytes
labz-bee-amber-green-soft-candidate-01.png            | 1536x1536 | RGBA | 301692 bytes
labz-bee-blue-soft-candidate-01.png                   | 1536x1536 | RGBA | 302779 bytes
labz-bee-gold-soft-candidate-01.png                   | 1536x1536 | RGBA | 303237 bytes
labz-lily-right-candidate-01.png                      | 1536x1536 | RGBA | 619121 bytes
labz-ora-pro-nobis-left-candidate-01.png              | 1536x1536 | RGBA | 556091 bytes
```

Directory size:

```text
2.2M /home/sanghop/axis/labz-ambient-candidates/flagfix_074_candidates
```

File type summary:

- Five candidate images are transparent PNG files with RGBA channels.
- Contact sheet is an RGB PNG review sheet.

## SHA256 Summary

```text
76ca9f404d8bec8d8edd36f6491f8617cf8ffc24979689c43b6a28127b6036b1  labz-ambient-candidates-contact-sheet-flagfix-074.png
fe582f4807e6379eeab94a485c1804dbb0c1ccec32667b8d54362c677b2c3d85  labz-bee-amber-green-soft-candidate-01.png
1ee8b5471a69da4f25df4d4472a3a7e549c99d77c3e680dd00c0e203576af2f1  labz-bee-blue-soft-candidate-01.png
5bb13bae29a9f30fe493852000afb0f4ae5bccd92aecb0e311b0948ac24e09ad  labz-bee-gold-soft-candidate-01.png
6a99805a1783e1062d7e2b053806a52d829e05384b6fd52e09ba7e489705618b  labz-lily-right-candidate-01.png
5bd16b5f5e8f28c0b13546ef075714fe556d7b6be706f3a97cced15709bbcce6  labz-ora-pro-nobis-left-candidate-01.png
```

Full external hash file:

- `/home/sanghop/axis/labz-ambient-candidates/flagfix_074_candidates/sha256sums.txt`

## Contact Sheet

Contact sheet path:

- `/home/sanghop/axis/labz-ambient-candidates/flagfix_074_candidates/labz-ambient-candidates-contact-sheet-flagfix-074.png`

The contact sheet places all five candidates on a neutral dark review background with filename labels.

## Tone And Style Notes

Generation approach:

- local procedural/vector-style transparent PNG candidates;
- no copyrighted source images used;
- no text embedded in candidate images;
- no animation;
- no site integration;
- no final WebP optimization yet.

Intended tone:

- quiet;
- soft;
- decorative;
- side-margin oriented;
- visually subordinate to the reading frame.

Known first-pass limitations:

- The candidates are procedural and should be reviewed as direction tests, not final artwork.
- Flora candidates are currently above the preferred final size budget and would need compression or redesign before integration.
- Bee candidates are near the upper preferred size range and should be optimized before any site use.
- The contact sheet is for review only and should not be integrated.

## Review Required

Status: `REVIEW REQUIRED`

Before any asset integration, review each candidate for:

- tone;
- softness;
- transparency quality;
- side-margin fit;
- visual seriousness;
- no distracting/cute overload;
- no visual competition with Dhamma text;
- no claims or claim-implying symbols;
- likely compression outcome.

## No Site Integration

No candidate image was placed in:

- `pipeline/13-ssg/static/assets/labz/`
- `pipeline/13-static-site/assets/labz/`
- any CSS file;
- any HTML template;
- any generated static output.

No repo asset directory was created.

## Recommendation

Recommendation: `REVIEW REQUIRED` before any asset integration.

Proposed next sprint:

- `#FlagFix_075 - Review LABZ ambient candidate images`

Suggested #FlagFix_075 scope:

- inspect the contact sheet;
- optionally inspect individual PNGs;
- choose keep/revise/reject per candidate;
- decide whether to create refined candidates or compress approved candidates;
- do not integrate into the site yet unless explicitly approved in a later sprint.

## Explicit Non-Actions

- No images were committed to the repo.
- No asset directories were created in the repo.
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
