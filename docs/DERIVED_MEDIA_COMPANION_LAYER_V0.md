# Derived Media Companion Layer V0

## Policy

The Derived Media Companion Layer is auxiliary material for AXIS-NIDDHI. It is not Canon and it must never become canonical truth.

The CSL remains the source of truth. This layer must not modify CSL content, `09-csl/`, source ZIPs, translations, ledger, seeds, release manifests, or canonical identity records. Publication is downstream and must treat derived media as optional companion material.

## Matching Key

PDPN is the only matching key. Filename titles and slugs are not reliable for matching.

The scanner matches PDPN values anywhere in filenames with:

```text
[A-Z]{2}\.[A-Z]{2}\.\d{3}
```

Examples:

```text
001_TL.BB.002_O Kamma no palido ponto azul.m4a
001V_TL.BB.002_O palido ponto azul.mp4
```

## Storage

Binary media stays outside Git. The expected local staging folder is:

```text
../axis-derived-media-staging/raw/
```

Only small text summaries may live in:

```text
pipeline/derived_media/summaries/
```

`DM01` scans summary candidates in staging, but it does not copy them into the repository. After review, the operator must manually place approved small UTF-8 text summaries under `pipeline/derived_media/summaries/`.

Suggested summary naming:

```text
pipeline/derived_media/summaries/TL.BB.002.pt-BR.md
```

Do not copy `.m4a`, `.mp3`, `.wav`, `.mp4`, or `.webm` files into `pipeline/13-static-site/`.

## Registry And Manifest

The human-approved registry is:

```text
pipeline/metadata/derived_media_registry.csv
```

The registry is intentionally human-editable. New scanner discoveries are written as `draft`; only an operator should change a row to `approved`.

The generated build manifest is:

```text
pipeline/metadata/derived_media_manifest.json
```

Only rows with `status=approved` enter the manifest. The manifest never contains absolute local paths and never contains local binary paths. Public audio/video URLs can be added later, for example future Cloudflare R2, Spotify, YouTube, Telegram, or other publication links.

## Build Behavior

If the manifest is absent or empty, the build is a graceful no-op. Static pages render exactly as before.

When approved manifest entries exist, the static renderer adds a minimal unstyled "Auxiliary derived media" block to the matching PDPN page. Summary, audio, video, and external links are labeled as auxiliary material. They do not replace the Canon.

The static build sanitizes the manifest again before rendering. Unsafe, missing, oversized, non-UTF-8, or hash-mismatched summaries are suppressed before templates see them, so missing summary files do not create broken page links.

## Commands

Run from `pipeline/`:

```bash
python3 scripts/tools/DM01_scan_derived_media.py --dry-run --verbose
python3 scripts/tools/DM01_scan_derived_media.py --apply
python3 scripts/tools/DM02_generate_derived_media_manifest.py --dry-run
python3 scripts/tools/DM02_generate_derived_media_manifest.py
```
