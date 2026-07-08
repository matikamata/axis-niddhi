# Derived Media Companion Layer V0 Plan

## Preservation Policy

This implementation follows the AXIS-NIDDHI preservation and derived-layer policy. Derived media is optional companion material. It is not Canon, and it must not become canonical truth.

## Canon Safety

This work does not silently change canonical content. It does not modify CSL content, `09-csl/`, source ZIPs, translations, ledger, seeds, release manifests, or canonical identity records.

The registry and manifest live outside canonical structures:

- `pipeline/metadata/derived_media_registry.csv`
- `pipeline/metadata/derived_media_manifest.json`
- `pipeline/derived_media/`

Static rendering consumes only the generated manifest and remains a no-op when the manifest is empty or absent.

## Rollback Path

To roll back the layer:

1. Remove the derived media files added in this feature branch.
2. Revert the static renderer/template changes that read `derived_media_manifest.json`.
3. Regenerate the static site.

Because no canonical content is changed, rollback does not require CSL repair, release manifest repair, ledger edits, or source restoration.

## Expected Files Changed

- `docs/DERIVED_MEDIA_COMPANION_LAYER_V0.md`
- `docs/DERIVED_MEDIA_COMPANION_LAYER_V0_PLAN.md`
- `.gitignore`
- `pipeline/metadata/derived_media_registry.csv`
- `pipeline/metadata/derived_media_manifest.json`
- `pipeline/derived_media/README.md`
- `pipeline/derived_media/summaries/.gitkeep`
- `pipeline/scripts/tools/DM01_scan_derived_media.py`
- `pipeline/scripts/tools/DM02_generate_derived_media_manifest.py`
- `pipeline/13-ssg/build.py`
- `pipeline/13-ssg/src/transformers/__init__.py`
- `pipeline/13-ssg/src/renderers/post_renderer.py`
- `pipeline/13-ssg/templates/post.html`

## Validation Checklist

- Run the scanner in dry-run mode against `../axis-derived-media-staging/raw/`.
- Generate the manifest from the header-only registry and confirm `{}`.
- Confirm the generator rejects invalid PDPN, unsafe URLs, local absolute paths, and forbidden secret markers.
- Confirm the static renderer is graceful when no approved derived media exists.
- Confirm no source ZIPs, CSL files, translations, ledger, seeds, release manifests, or canonical identity records changed.
- Confirm no binary media files were copied into Git or `pipeline/13-static-site/`.
