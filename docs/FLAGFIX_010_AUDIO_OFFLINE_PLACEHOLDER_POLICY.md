# FlagFix 010 — Audio Offline Placeholder and External Resolution Policy

## Status

Planning / review policy only.

No renderer, CSL, HTML, CSS, JavaScript, asset map, audio, download, external URL, or static-site output changes are authorized by this document.

## Problem

AXIS-NIDDHI pages may reference audio assets, pronunciation aids, embedded players, or external audio resources that behave differently depending on publication context.

Risks include:

- audio files not bundled for offline/static review;
- oversized audio assets exceeding static hosting limits;
- broken local or historical WordPress audio URLs;
- placeholders appearing in the wrong language;
- external audio links losing source traceability;
- browser/player behavior differing between screen, print, and offline use;
- future multilingual pages needing localized explanatory placeholders;
- audio-related UI changes accidentally modifying doctrinal content.

## Principle

Audio is supporting media, not canonical text.

Audio handling must preserve source traceability while avoiding broken or misleading user-facing playback states.

No audio placeholder should imply that missing audio was intentionally removed, translated, corrected, or doctrinally changed.

## Protected behavior

The following must not be changed automatically:

- canonical source references to original audio assets;
- CSL metadata that records audio origin;
- known PureDhamma.net upload URLs;
- existing static page text;
- language-specific content blocks;
- print review content;
- audio labels or pronunciation notes that contain Pāli terms.

## Placeholder policy

If an audio asset is unavailable, externalized, oversized, or intentionally not bundled, future implementation may display a conservative placeholder only after review.

A placeholder should communicate:

- audio is unavailable in the current static/offline context;
- the source reference remains preserved;
- the user may need to access the original external source;
- no doctrinal or translation change is implied.

## Language policy

Placeholder language must match the page context where possible.

Review-sensitive cases:

- English page with English placeholder;
- Portuguese page with Portuguese placeholder;
- mixed EN/PT review pages;
- print output where playback UI is irrelevant;
- archive/listing pages where audio status should not clutter navigation.

## External resolution policy

External audio resolution must be conservative.

Allowed future strategies, after review:

1. preserve original URL in metadata;
2. rewrite oversized or non-bundled audio to an approved external base URL;
3. display a source-preserving placeholder when playback is unavailable;
4. keep offline static output readable even without audio;
5. document each externalization rule.

Forbidden without separate approved implementation:

1. invent replacement audio;
2. upload audio to a new host without review;
3. rewrite source URLs silently;
4. translate Pāli pronunciation content mechanically;
5. hide broken audio in a way that removes source traceability;
6. modify canonical CSL text or metadata as a side effect.

## Print policy

Print output should not depend on playable audio.

Future print handling may:

- suppress interactive controls;
- show a compact audio marker;
- show source/reference status;
- avoid large empty boxes or broken controls.

Any such behavior requires separate review and implementation.

## Review requirements

Before implementation, reviewers should identify:

- affected PD#PN;
- source audio URL;
- local/static audio URL if present;
- whether audio is bundled, externalized, oversized, missing, or broken;
- affected language context;
- desired placeholder wording;
- print behavior;
- decision.

## Acceptance criteria for this policy

This policy is complete when:

- audio offline/external resolution risks are documented;
- placeholder language rules are documented;
- source traceability requirements are documented;
- no renderer, CSL, HTML, CSS, JavaScript, asset map, audio, download, external URL, or static-site output is changed.

## Next step

Create or extend a human-review audio/media matrix before implementing any placeholder or URL resolution behavior.
