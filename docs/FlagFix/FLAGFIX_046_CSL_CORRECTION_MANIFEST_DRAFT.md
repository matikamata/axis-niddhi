# FlagFix 046 - CSL Correction Manifest Draft

Date: 2026-05-18

## Scope

This sprint created a tracked manifest draft for known CSL metadata corrections applied on disk during #FlagFix_028 and #FlagFix_037 through #FlagFix_043.

No validator, apply script, `.gitignore` change, CSL edit, static edit, build, pipeline, deploy, DeepL call, or Vitrine promotion was performed.

## Manifest

Manifest path:

- `review/csl-corrections/csl_metadata_corrections_manifest_v1.json`

Manifest purpose:

- preserve intended CSL metadata title corrections in tracked form;
- make future read-only validation possible;
- avoid relying only on ignored `pipeline/09-csl` workspace state.

## Correction Count

Corrections recorded: 25

Breakdown:

- #FlagFix_028: 1 correction
- #FlagFix_037: 1 correction
- #FlagFix_039: 5 corrections
- #FlagFix_040: 5 corrections
- #FlagFix_041: 5 corrections
- #FlagFix_042: 3 corrections
- #FlagFix_043: 5 corrections

## Source FlagFixes Covered

- #028: `LD.AA.000` PT title contamination cleanup.
- #037: `BA.AA.004` EN title diacritic corruption cleanup.
- #039: EN title correction batch 1.
- #040: EN title correction batch 2.
- #041: EN title correction batch 3.
- #042: final EN title correction batch.
- #043: PT title corruption cleanup.

## Current Limitations

The manifest is not an apply mechanism.

No validator exists yet. This means the manifest is reviewable documentation/data, but it does not yet automatically compare current `pipeline/09-csl` values against expected corrected values.

No apply script exists. This is intentional. Any future write-capable remediation must be reviewed after the manifest and read-only validator are accepted.

## Next Recommended Sprint

Suggested next sprint:

`#FlagFix_047 - CSL correction manifest read-only validator`

Recommended scope:

- read the tracked manifest;
- check that each referenced `identity.json` exists;
- compare `json_path` current value to `new_value`;
- report match/mismatch/missing/JSON error counts;
- exit nonzero on mismatches;
- do not write to CSL;
- do not create an apply script.

## JSON Validation

The manifest was validated with:

```bash
python3 -m json.tool review/csl-corrections/csl_metadata_corrections_manifest_v1.json >/tmp/csl_manifest_v1.pretty.json
```

## No-Change Confirmations

- Did not touch `/home/sanghop/axis/axis-niddhi-published`.
- Did not update Netlify/Vitrine.
- Did not run build, pipeline, or deploy.
- Did not call DeepL.
- Did not translate anything.
- Did not modify CSL content.
- Did not modify static artifacts.
- Did not modify metadata CSVs.
- Did not modify `Translation_Control_Center.csv`.
- Did not modify SP10/SP11 behavior.
- Did not change `.gitignore`.
- Did not create a validator.
- Did not create an apply script.
