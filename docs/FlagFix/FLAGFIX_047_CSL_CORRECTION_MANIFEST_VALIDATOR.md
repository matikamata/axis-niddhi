# FlagFix 047 - CSL Correction Manifest Validator

Date: 2026-05-18

## Scope

This sprint added a read-only validator for the tracked CSL correction manifest created in #FlagFix_046.

The validator compares manifest `new_value` entries against the current local CSL metadata under `pipeline/09-csl`.

## Files

Validator script:

- `pipeline/scripts/tools/validate_csl_correction_manifest.py`

Manifest path:

- `review/csl-corrections/csl_metadata_corrections_manifest_v1.json`

## Behavior

The validator:

- loads the tracked manifest JSON;
- validates required top-level keys;
- validates required correction fields;
- supports `titles.en` and `titles.pt` JSON paths;
- reads each target `identity.json`;
- compares the current value to manifest `new_value`;
- prints one status line per correction;
- prints a concise summary;
- does not write to CSL or any other project file.

Status values:

- `MATCH`
- `MISMATCH`
- `MISSING_FILE`
- `MISSING_PATH`

Exit codes:

- `0`: all corrections match current local CSL metadata.
- `1`: validation completed, but mismatches or missing entries were found.
- `2`: invalid manifest or fatal manifest read error.

## Actual Validation Result

Command run:

```bash
python3 pipeline/scripts/tools/validate_csl_correction_manifest.py
echo "exit_code=$?"
```

Result:

```text
summary: total=25 match=25 mismatch=0 missing_file=0 missing_path=0
exit_code=0
```

This confirms that the current local CSL metadata matches the tracked correction manifest.

## Next Recommended Sprint

A future sprint may consider an apply script only after reviewing the manifest and validator behavior.

Recommended next step before any apply script:

- add a small negative-fixture test or documented dry-run mismatch example;
- keep any future apply mode separate from this read-only validator;
- continue avoiding `.gitignore` changes until CSL ownership is decided.

## No-Change Confirmations

- Did not create an apply script.
- Did not modify CSL content.
- Did not touch `/home/sanghop/axis/axis-niddhi-published`.
- Did not update Netlify/Vitrine.
- Did not run build, pipeline, or deploy.
- Did not call DeepL.
- Did not translate anything.
- Did not modify static artifacts.
- Did not modify metadata CSVs.
- Did not modify `Translation_Control_Center.csv`.
- Did not modify SP10/SP11 behavior.
- Did not change `.gitignore`.
