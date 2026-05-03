# FlagFix 015 — YouTube Print Marker Policy

## Status

Planning / review policy only.

No renderer, CSL, HTML, CSS, JavaScript, asset map, embed, YouTube, print, or static-site output changes are authorized by this document.

## Problem

Some AXIS-NIDDHI pages may contain YouTube embeds or embed variants that do not communicate clearly in printed review output.

Risks include:

- embedded videos disappearing silently in print;
- print reviewers missing that a video existed on the source page;
- iframe variants behaving differently across browsers;
- video placeholders appearing in the wrong language;
- YouTube links losing source traceability;
- print CSS fixes accidentally affecting non-video media;
- future embed handling changing source evidence without review.

## Principle

A YouTube embed is supporting media and source context.

In print or offline review contexts, the user should be able to see that a video/embed existed, without confusing the marker for canonical text.

## Protected behavior

Future implementation must preserve:

- source URL traceability;
- original embed intent;
- visible indication in print when a video cannot render;
- language-appropriate placeholder wording;
- separation between canonical article text and media marker;
- no invented title, description, or transcript unless human-reviewed.

## Review-sensitive cases

The following require human review before implementation:

- YouTube iframe embeds;
- legacy WordPress embed shortcodes;
- plain YouTube links intended as embeds;
- missing or malformed embed URLs;
- video placeholders in print;
- video placeholders in pt-BR pages;
- pages where video context affects comprehension.

## Forbidden actions

Without a separate approved implementation issue, do not:

1. rewrite embed HTML;
2. change renderer behavior;
3. change CSS print rules;
4. alter canonical CSL content;
5. infer missing video titles;
6. generate transcripts;
7. replace YouTube URLs;
8. remove embeds from output;
9. modify static-site generated files;
10. treat video markers as article body text.

## Allowed future implementation shape

A future implementation may be proposed only after review and should be minimal:

- detect video/embed blocks;
- preserve original URL;
- show a print-only marker;
- keep marker visually distinct from article text;
- localize marker language when page language is known;
- avoid modifying canonical content.

## Acceptance criteria for this policy

- Policy document exists.
- YouTube/embed print marker risks are documented.
- No renderer, CSL, HTML, CSS, JavaScript, asset map, embed, YouTube, print, or static-site output is changed.
- Future implementation remains blocked pending Batch 04 media review rules.
