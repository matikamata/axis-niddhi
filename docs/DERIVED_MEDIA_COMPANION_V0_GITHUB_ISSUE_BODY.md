# Derived Media Companion Layer V0

This issue tracks the AXIS-NIDDHI Derived Media Companion Layer V0.

## Scope

- Derived layer only; not Canon.
- CSL remains the source of truth.
- Publication consumes derived media downstream.
- NotebookLM summaries/audio/video are auxiliary material and must be labeled as such.

## Contract

- Human-editable registry CSV: `pipeline/metadata/derived_media_registry.csv`
- Generated manifest JSON: `pipeline/metadata/derived_media_manifest.json`
- Only `approved` registry rows enter the manifest.
- No binary media files in Git.
- No `.m4a`, `.mp4`, `.webm`, `.wav`, or `.mp3` files should be committed.
- No absolute local paths or `file://` URLs in the generated manifest.
- Build must be graceful no-op when the manifest is absent or empty.

## Deferred Publication Links

Future Cloudflare R2, Spotify, YouTube, and Telegram URLs can be filled manually in the registry after operator approval.

## Audit

Audit document:

```text
docs/DERIVED_MEDIA_COMPANION_V0_AUDIT_20260708.md
```

## Deployment

No production deploy requested.

Do not merge to `main` from this issue without explicit operator approval.
