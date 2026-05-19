# FlagFix 073 - LABZ Ambient Candidate Image Generation Plan

Date: 2026-05-19

## Goal

Plan candidate image generation outside the repository before any LABZ ambient asset integration.

This is a documentation-only planning sprint. It creates no images, no asset directories, and no CSS/HTML/JS/static changes.

## Context

Latest checkpoint:

- `checkpoint/flagfix-072-labz-ambient-visual-asset-design-plan-20260519`

Current LABZ state:

- Source-only side layer exists.
- CSS placeholder motifs exist.
- No final images have been created.
- No CSS image integration has happened.
- No static regeneration has happened.

Recommended future source asset path from #FlagFix_072:

- `pipeline/13-ssg/static/assets/labz/`

## Candidate Image Set

First candidate set:

- Ora-pro-nobis flower cluster, soft left-side composition.
- White/gold lily, soft right-side composition.
- Gold bee, small decorative accent.
- Blue bee, small decorative accent.
- Amber/green bee, small decorative accent.

The flora candidates should be designed as side-margin compositions rather than central illustrations. The bee candidates should be small accents, not characters or mascots.

## External Working Directory

Recommended candidate working directory outside all Git repositories:

- `/home/sanghop/axis/labz-ambient-candidates/flagfix_074_candidates/`

This directory should be used in the next sprint only if candidate image generation is explicitly approved.

Do not create this directory in #FlagFix_073.

## Style Constraints

Candidate images should follow these constraints:

- Transparent background preferred.
- Quiet, noble, contemplative.
- No text.
- No symbols that imply claims.
- No medical, therapy, cognitive, subliminal, performance, wellness, healing, or accelerated-learning language.
- Soft edges.
- No aggressive contrast.
- No visual clutter.
- Suitable for side margins.
- Should not compete with Dhamma text.
- Should not resemble badges, alerts, UI controls, mascots, or reward icons.
- Should remain visually subordinate to the reading frame.

Any prompt or generation note should describe the assets as decorative ambient imagery only.

## Technical Target

Initial candidates:

- PNG or WebP with transparency.
- Source dimensions around `1024x1024` or `1536x1536`.
- Later compressed to WebP after review.
- Target final file size ideally under `200-350 KB` per decorative image.
- No animation in the first version.
- No embedded text.
- No EXIF/metadata dependency.

Suggested candidate export approach:

- Keep raw candidates outside repo.
- Keep any prompt/reference notes outside repo or in a later approved review artifact.
- Do not optimize into final production assets until visual review passes.
- Do not add files to `pipeline/13-ssg/static/assets/labz/` until a later integration sprint.

## Review Checklist

Each candidate should be reviewed for:

- Tone.
- Softness.
- Transparency quality.
- Readability impact.
- Side-margin fit.
- Mobile/print non-impact once integrated.
- Asset size.
- Visual seriousness.
- No claims.
- No distracting anthropomorphic or cute overload.
- No bright flicker impression.
- No accidental icon/button affordance.
- No conflict with existing stardust palette.

Suggested review method:

- Place candidates on a dark/stardust-like background in a contact sheet.
- Preview left/right side margin composition near a mock reading frame.
- Compare at full desktop size and laptop width.
- Reject any candidate that draws attention away from text.

## Proposed Next Sprint

`#FlagFix_074 - Generate LABZ ambient candidate images outside repo`

The next sprint should:

- Create images outside repo only.
- Use `/home/sanghop/axis/labz-ambient-candidates/flagfix_074_candidates/`.
- Generate/check dimensions and file sizes.
- Create a contact sheet or visual review sheet if possible.
- Record candidate paths, dimensions, file sizes, and SHA256 values.
- Not integrate into the site yet.
- Not create `pipeline/13-ssg/static/assets/labz/` yet unless a later sprint explicitly approves integration.

## Recommendation

Recommendation: GO WITH GUARDS.

Proceed to candidate generation only if it remains outside the repo and is treated as visual exploration. The site should not receive image assets, CSS image wiring, generated static output, or deployment changes until candidates pass visual review.

## Explicit Non-Actions

- No images were created.
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
