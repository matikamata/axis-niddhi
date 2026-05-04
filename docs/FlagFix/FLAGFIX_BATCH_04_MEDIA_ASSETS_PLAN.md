# FlagFix Batch 04 — Media and Assets

Status: PLANNING ONLY  
Scope: media, images, flowcharts, external assets, print/video traceability  
Do not implement code from this document without a separate branch and review.

---

## 1. Purpose

This batch tracks media and asset issues discovered during print-review and site-review of AXIS-NIDDHI.

The goal is not to hide broken or untranslated media, but to preserve evidence, improve reviewer usability, and create a future-proof path for human/curatorial correction.

AXIS-NIDDHI must treat media artifacts as part of the transmission record.

---

## 2. Included FlagFix Issues

### FlagFix 005 — Translatable image / flowchart assets

Problem:

Many original PureDhamma.net images, flowcharts, diagrams, PDFs, and embedded visual assets contain English text inside raster/vector media. These are not normal HTML text and cannot be translated by DeepL or the current translation pipeline.

Examples include images such as `climbers.png`, where labels like “Grapevine / Pea / Money Plant” are embedded directly in the image.

Current impact:

- Portuguese readers may encounter English-only diagrams.
- Reviewers may think the translation pipeline missed text.
- Replacing such media automatically is risky because diagrams often carry doctrinal structure.
- Editing all visual assets manually is a large future human effort.

Recommended future strategy:

- Do not auto-translate image text.
- Preserve original media as canonical evidence.
- Add optional HTML captions near affected media explaining that the visual asset remains in English and requires future human translation/redrawing.
- Invite future contributors (“Abelhas”) to help translate/redraw diagrams.
- Track each media asset in a future media registry with:
  - PD#PN
  - original media filename
  - original PureDhamma.net URL
  - local/static URL
  - language status
  - needs redraw?
  - needs doctrinal review?
  - replacement candidate path
  - human reviewer approval status

---

### FlagFix 010 — Audio offline placeholder language and external resolution

Problem:

Some audio placeholders or fallback messages appear with language mismatch, for example Portuguese text inside en-US pages.

Observed issue:

`[áudio externo indisponível offline]`

This is confusing because:

- en-US pages should not display pt-BR-only UI messages.
- Some audio files are intentionally external because large files over Cloudflare Pages limits are resolved against PureDhamma.net or other stable external URLs.
- The current placeholder may suggest the audio is broken even when the browser/local environment is the actual issue.

Current impact:

- User may assume valuable audio is missing.
- Revisor may flag a false negative.
- The site does not yet clearly distinguish:
  - local audio available
  - external audio available
  - external audio unavailable
  - offline limitation
  - legacy unresolved audio evidence

Recommended future strategy:

- Make audio fallback messages language-aware.
- Preserve audio traceability even when playback fails.
- Never hide missing audio silently.
- Prefer explicit, human-readable diagnostic states.
- Future UI could show:
  - Audio available locally
  - Audio available from PureDhamma.net
  - External audio unavailable in this environment
  - Legacy media reference preserved for review
- Consider a future audio registry similar to the media registry.

---

### FlagFix 014 — Image rendering size, centering, and zoom

Problem:

Some images render too small or visually off-center in the static site.

Current impact:

- Some diagrams are difficult to read.
- Print copies may waste space while still showing images too small.
- Reviewers may not know they can open the image separately.
- The same CSS rule may not work for every image because diagrams, inline icons, and large flowcharts have different needs.

Recommended future strategy:

- Audit rendered images by size, aspect ratio, and page context.
- Improve default image centering and max-width rules.
- Avoid stretching small images beyond useful resolution.
- Add “open image in new tab” behavior where appropriate.
- Consider optional caption text:
  - “Click/open image in a new tab for larger view.”
  - In print: “Image may contain embedded English text; original visual asset preserved.”
- Future implementation should avoid harming:
  - inline icons
  - small decorative images
  - screenshots
  - doctrinal diagrams
  - legacy PureDhamma media

---

### FlagFix 015 — YouTube print marker missing for embed variants

Problem:

Some pages contain video embeds that disappear in print without leaving a traceability marker.

Already partially fixed:

- Standard YouTube iframe markers were added for print review.
- Print output now shows a box when recognized YouTube iframes are present.

Remaining risk:

Some embeds may not use the exact same iframe structure or selector pattern.

Possible variants:

- iframe with nonstandard src
- lazy-loaded YouTube embed
- WordPress shortcode-generated embed
- oEmbed wrapper
- custom div wrapper
- legacy embed HTML
- missing title attribute
- privacy-enhanced YouTube domain
- malformed migrated embed

Current impact:

- Printed review copies may lose evidence that a video existed.
- Future archival readers may not know the page contained video material.
- Review traceability is incomplete.

Recommended future strategy:

- Expand detection beyond `iframe[src*="youtube"]`.
- Detect:
  - `youtube.com`
  - `youtu.be`
  - `youtube-nocookie.com`
  - embed wrappers
  - oEmbed blocks
  - known WordPress video containers
- Preserve visible print marker with:
  - media type
  - title if available
  - full URL if available
  - PD#PN context
  - note that video was omitted in print
- Avoid inventing titles.
- If title is unknown, say “Title unavailable in source HTML.”

---

## 3. Architectural Rule

Media is not decoration.

In AXIS-NIDDHI, media can be:

- doctrinal explanation
- chanting/audio pronunciation
- historical evidence
- study aid
- visual map
- embedded teaching context
- source traceability artifact

Therefore:

- Do not delete unresolved media references.
- Do not silently hide broken media.
- Do not auto-translate media text without human review.
- Do not replace original PureDhamma media without preserving provenance.
- Prefer evidence blocks, captions, registries, and explicit review states.

---

## 4. Proposed Future Work Blocks

### Block A — Media Registry

Create a canonical media registry under metadata, for example:

`metadata/media_registry.json`

Fields:

- pdpn
- source_url
- static_url
- media_type
- filename
- language
- status
- requires_translation
- requires_redraw
- requires_audio_review
- print_behavior
- reviewer_notes

---

### Block B — Print Media Traceability

Standardize print behavior:

- videos become print marker boxes
- unresolved shortcodes become evidence blocks
- images remain visible unless impossible
- English-only diagrams receive optional explanatory note
- large/external assets show stable source URL where useful

---

### Block C — Media UI Enhancements

Possible future site behavior:

- click image to open in new tab
- optional zoom overlay
- caption for untranslated visual assets
- external audio diagnostics
- media evidence block styling
- “help translate/redraw this diagram” invitation

---

### Block D — Human Review Workflow

Create a future spreadsheet or CSV export with:

- PD#PN
- page URL
- media filename
- media URL
- issue type
- priority
- proposed action
- reviewer
- approval status

---

## 5. Priority Recommendation

Suggested order:

1. Keep existing evidence preservation layer stable.
2. Audit all media assets and classify them.
3. Fix print markers for all video embed variants.
4. Improve image centering/open-in-new-tab behavior.
5. Add captions/invitations for English-only visual assets.
6. Build a human media review matrix.

---

## 6. Success Criteria

This batch is successful when:

- no media reference disappears silently
- printed pages preserve video/media traceability
- English-only diagrams are clearly marked as preserved assets requiring future work
- audio fallback messages are language-aware
- large/external media behavior is explicit
- future contributors can identify useful media tasks without touching canonical text

---

## 7. Non-Goals

This batch does not attempt to:

- redraw all flowcharts
- translate embedded image text automatically
- replace PureDhamma.net media
- solve all audio hosting permanently
- run a full production rebuild without approved CSL provenance

---

## 8. Related Issues

- FlagFix 005
- FlagFix 010
- FlagFix 014
- FlagFix 015

Related planning:

- `docs/FLAGFIX_MEDIA_SHORTCODE_PRESERVATION_PLAN.md`
- `docs/FLAGFIX_023_PRODUCTION_BUILD_INPUT_CONTRACT.md`
