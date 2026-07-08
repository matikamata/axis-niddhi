# AXIS-NIDDHI Derived Media

This folder is a derivative companion layer. It is not Canon.

Rules:

- The CSL remains the source of truth.
- Derived media must never modify `09-csl/`, source ZIPs, translations, ledger, seeds, release manifests, or canonical identity records.
- Every summary, audio item, video item, or external link must cite the Canon through PDPN.
- This layer must be rebuildable or disposable.
- Binary media files must not be committed here.
- Only small text summaries may live under `derived_media/summaries/`.

Operator workflow:

1. Keep generated audio/video binaries outside Git, usually in `../axis-derived-media-staging/raw/`.
2. Use `scripts/tools/DM01_scan_derived_media.py` to inspect local candidates. It scans summaries but does not copy them here.
3. Manually place approved small UTF-8 summaries under `derived_media/summaries/`, for example `derived_media/summaries/TL.BB.002.pt-BR.md`.
4. Manually review and approve rows in `metadata/derived_media_registry.csv`.
5. Run `scripts/tools/DM02_generate_derived_media_manifest.py --dry-run` before writing the manifest.
6. Run `scripts/tools/DM02_generate_derived_media_manifest.py` to build `metadata/derived_media_manifest.json`.
7. The static build suppresses unsafe or missing summary links before rendering pages.
