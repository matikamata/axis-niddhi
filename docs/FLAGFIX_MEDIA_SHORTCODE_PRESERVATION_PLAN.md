# FlagFix — Media Shortcode Preservation Layer

## Status

Planning document only. No production behavior changes in this branch.

## Problem

Some WordPress media/download shortcodes are leaking into generated AXIS-NIDDHI static pages as literal text, for example:

```text
[easy_media_download url="..." text="Baixar" width="90" target="_blank"]
````

This is not merely visual noise. It is preserved source evidence pointing to media/download assets that may contain valuable doctrinal, audio, diagram, or review material.

## Architectural Decision

Do not hide these shortcodes with CSS.

Do not delete them from generated pages.

Do not treat them as garbage.

Instead, convert recognized source shortcodes into explicit AXIS preservation blocks that:

* preserve the original source signal;
* expose the media URL when available;
* distinguish resolved vs unresolved media;
* remain visible on screen;
* print in a compact archival form;
* avoid corrupting URLs through Pāli/glossary highlighting;
* allow future resolution to local assets, external buckets, Google Drive, YouTube, Spotify, or PureDhamma source URLs.

## Target Component

Future generated HTML should use a semantic block similar to:

```html
<div class="axis-media-preservation axis-media-unresolved">
  <strong>Media preserved from source</strong>
  <p>Original WordPress media shortcode detected.</p>
  <a href="..." target="_blank" rel="noopener noreferrer">Open preserved media source</a>
</div>
```

## Non-Goals

This branch should not:

* remove working audio players;
* hide media warnings;
* replace media with Spotify/YouTube yet;
* change CSL canonical content directly unless explicitly planned;
* introduce non-deterministic network fetches during build;
* silently download remote assets.

## Root-Cause Hypothesis

The static site generation pipeline currently passes WordPress shortcodes through as text after translation/rendering, instead of normalizing them into a structured media-preservation component.

Additionally, some URL-like shortcode content may be passing through glossary/Pāli transformation, causing markup corruption inside URLs.

## Proposed Implementation Phases

### Phase 1 — Inventory

Search generated pages and CSL/source layers for shortcode leakage.

```bash
grep -Rni "\[easy_media_download" pipeline/13-static-site pipeline/09-csl 2>/dev/null || true
grep -Rni "drive.google.com/open" pipeline/13-static-site pipeline/09-csl 2>/dev/null || true
grep -Rni "easy_media_download" pipeline/13-ssg pipeline/scripts 2>/dev/null || true
```

### Phase 2 — Parser

Add a deterministic shortcode parser that extracts:

* shortcode name;
* url;
* text label;
* width;
* target;
* raw original shortcode;
* parse status.

If URL cannot be extracted, preserve raw shortcode inside an unresolved block.

### Phase 3 — Renderer

Render recognized media shortcodes as AXIS media preservation blocks.

Expected states:

* `axis-media-resolved`
* `axis-media-external`
* `axis-media-unresolved`
* `axis-media-malformed`

### Phase 4 — CSS

Add minimal screen and print CSS.

Screen behavior:

* visible;
* calm technical box;
* not alarming;
* useful to reviewers.

Print behavior:

* compact;
* preserves source URL if short enough;
* wraps long URLs safely;
* does not waste pages.

### Phase 5 — Safety Tests

Acceptance checks:

* no literal `[easy_media_download` appears in generated HTML;
* media URL is preserved somewhere in generated HTML;
* existing working audio remains working;
* no Pāli/glossary markup appears inside URLs;
* TL.EE.003 no longer shows raw shortcode text;
* print preview remains compact.

## Acceptance Tests

```bash
python3 pipeline/13-ssg/build.py

grep -Rni "\[easy_media_download" pipeline/13-static-site/pages && exit 1 || echo "OK: no raw easy_media_download shortcode leaked"

grep -Rni "axis-media-preservation" pipeline/13-static-site/pages | head -20

grep -Rni "<span[^>]*>.*drive.google.com\|drive.google.com.*</span>" pipeline/13-static-site/pages && exit 1 || echo "OK: no obvious glossary span inside media URL"
```

## Rollback

Revert only the media shortcode branch/commit. This should be isolated from print UX and title/metadata work.

## Related FlagFix Issues

* FlagFix 010 — Audio offline placeholder language and external resolution
* FlagFix 022 — raw media shortcode leakage / media preservation
* FlagFix 014 — image rendering and asset resolution
* FlagFix 015 — YouTube print marker variants

## Guiding Principle

A leaked shortcode is not trash.

It is unresolved preservation evidence.

The AXIS-NIDDHI engine should make that evidence explicit, stable, reviewable, and eventually resolvable.
