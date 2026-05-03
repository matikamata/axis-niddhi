# FlagFix 014 — Image Rendering Size, Centering, and Zoom Policy

## Status

Planning / review policy only.

No renderer, CSL, HTML, CSS, JavaScript, asset map, image, OCR, translation, or static-site output changes are authorized by this document.

## Problem

Some AXIS-NIDDHI images may render with poor sizing, centering, zoom behavior, print behavior, or visual alignment.

Risks include:

- images appearing too small to read;
- images overflowing content width;
- images not centered consistently;
- diagrams losing readability in print;
- screenshots becoming unclear on mobile or PDF output;
- CSS fixes accidentally affecting all images globally;
- image presentation changes being mistaken for source-content changes;
- future zoom/lightbox behavior altering review workflows.

## Principle

Image rendering is presentation, not canonical content.

Any future visual fix must preserve the original image asset and source traceability unless a separate human-reviewed asset replacement is approved.

## Review-sensitive cases

The following cases require review before implementation:

- diagrams with doctrinal labels;
- images containing Pāli terms;
- flowcharts or causal diagrams;
- screenshots with embedded text;
- large images that need constrained display width;
- small images that need readable scaling;
- images that behave differently on screen and print;
- images where cropping, centering, or zoom could change interpretation.

## Allowed future implementation types

Only after review, future implementation may consider:

1. CSS-only max-width improvements;
2. centering rules scoped to content images;
3. print-specific image sizing rules;
4. optional click-to-zoom behavior;
5. lightbox/zoom behavior that preserves the original image URL;
6. per-image exception metadata;
7. accessibility captions or alt-text review.

## Forbidden automatic actions

Do not automatically:

1. crop images;
2. redraw images;
3. OCR and replace embedded text;
4. translate image text;
5. compress source assets destructively;
6. replace source images with generated images;
7. apply global CSS that changes layout unexpectedly;
8. modify CSL content to fix presentation-only issues.

## Acceptance criteria for this policy

- Image rendering risks are documented.
- Source image preservation is explicitly required.
- Future CSS/zoom fixes are blocked pending review.
- No renderer, CSL, HTML, CSS, JavaScript, asset map, image, OCR, translation, or static-site output is changed.
