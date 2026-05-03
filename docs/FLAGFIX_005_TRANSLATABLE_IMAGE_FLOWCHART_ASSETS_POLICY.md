# FlagFix 005 — Translatable Image and Flowchart Assets Policy

## Status

Planning / review policy only.

No renderer, CSL, HTML, CSS, JavaScript, asset map, image, OCR, translation, or static-site output changes are authorized by this document.

## Problem

Some source images, diagrams, screenshots, and flowcharts may contain embedded English text or doctrinal labels that are not directly translatable by the normal HTML/text translation pipeline.

These assets require special handling because they may contain:

- doctrinal terms;
- Pāli terms;
- arrows, sequence logic, or causal structure;
- labels that must preserve source meaning;
- visual layout that affects comprehension;
- mixed image/text evidence;
- captions or surrounding explanation that may not fully reproduce the text embedded in the image.

## Principle

A text-bearing image is source-bound evidence.

It must not be automatically redrawn, translated, OCR-corrected, compressed, replaced, cropped, or visually normalized without human review.

## Asset categories

The following should be treated as review-sensitive:

- doctrinal flowcharts;
- diagrams with arrows or causal relations;
- screenshots containing explanatory text;
- images with embedded English text;
- images containing Pāli terms;
- tables exported as images;
- visual summaries of Dhamma concepts;
- handwritten or low-resolution source images;
- any image where text is part of the teaching, not decoration.

## Required review fields

Future inventory should capture, at minimum:

- PD#PN;
- source image URL/path;
- AXIS static-site image path;
- asset type;
- whether embedded text exists;
- whether Pāli/doctrinal terms appear;
- whether translation is needed;
- whether redraw is needed;
- whether original image must remain visible;
- reviewer note;
- final decision.

## Allowed future treatments

Only after review, an asset may be classified as one of:

1. preserve original only;
2. preserve original plus translated caption;
3. preserve original plus translated transcript below;
4. preserve original plus reviewed translated replacement image;
5. preserve original plus side-by-side translated diagram;
6. needs doctrinal review before any visual change.

## Forbidden automatic behavior

Do not automatically:

- OCR and replace embedded image text;
- translate image text mechanically;
- redraw flowcharts;
- change arrows, ordering, or grouping;
- crop out source text;
- remove original images after creating translated versions;
- normalize Pāli terms inside images;
- replace image semantics with approximate summaries.

## Preservation rule

The original source image must remain traceable.

If a translated or redrawn version is ever introduced, it must be treated as a derivative review artifact, not as a silent replacement for the source asset.

## Recommended implementation sequence

Future implementation, if approved, should proceed in this order:

1. create an inventory CSV for text-bearing images;
2. seed the inventory with a small pilot set;
3. classify assets by review type;
4. add human reviewer notes;
5. decide whether captions/transcripts are enough;
6. only then consider rendering or asset pipeline changes.

## Acceptance criteria for this policy

- Policy document exists.
- Text-bearing image assets are classified as source-bound review evidence.
- No image, renderer, CSL, OCR, translation, or static-site output is changed.
- Future implementation remains blocked pending human-reviewed asset inventory.
