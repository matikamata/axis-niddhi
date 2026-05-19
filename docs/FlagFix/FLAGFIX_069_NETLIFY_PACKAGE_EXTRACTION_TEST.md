# FlagFix 069 - Netlify Package Extraction Test

Date: 2026-05-19

## Context

Latest checkpoint:

- `checkpoint/flagfix-068-netlify-vitrine-deployment-package-20260519`

#FlagFix_068 created the audit-ready Netlify Vitrine deployment package. This sprint tested package integrity by verifying SHA256, extracting into `/tmp`, comparing the extracted payload to the approved source payload, and checking key files and corrected strings.

No upload or deployment was performed.

## Package

Package path:

- `/home/sanghop/axis/vitrine-deployment-packages/flagfix_068_20260519_060749/niddhi-netlify-vitrine-static-site-flagfix-068.tar.gz`

Package existence:

- `package_exists=yes`

SHA256 result:

```text
36cb0f2ee4feff4f45590684390b70b016d9e0246aac215f4af6f491b4272589  /home/sanghop/axis/vitrine-deployment-packages/flagfix_068_20260519_060749/niddhi-netlify-vitrine-static-site-flagfix-068.tar.gz
```

Expected SHA256:

```text
36cb0f2ee4feff4f45590684390b70b016d9e0246aac215f4af6f491b4272589
```

Result:

- SHA256 matches expected.

## Extraction

Extraction directory:

- `/tmp/flagfix_069_netlify_package_extract`

Extraction command:

```bash
tar -xzf "$PKG" -C "$EXTRACT"
```

Extracted payload:

- File count: `3082`
- Size: `807M`

Expected file count:

- `3082`

Result:

- Extracted file count matches expected.

## Source Comparison

Source payload:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Extracted payload:

- `/tmp/flagfix_069_netlify_package_extract`

Comparison result:

- `diff -qr` output lines: `0`
- Extracted payload is identical to the approved source payload.

## Key File Checks

All required key files were present in the extracted package:

```text
EXISTS archive.html
EXISTS index.json
EXISTS search_index.json
EXISTS pages/LD.AA.000/index.html
EXISTS pages/BA.AA.004/index.html
EXISTS assets/BodhiCircuitLeaf.png
```

## String Checks

Stale strings checked:

- `Vivendo il Dhamma`
- `Viparie1B987Ama Two Meanings`
- `pending translation / pendente de tradução`

Result:

- No stale string hits found in the extracted package.

Corrected strings checked:

- `Vivendo o Dhamma`
- `Vipariṇāma Two Meanings`
- `Awaiting translation / Aguardando tradução`

Result:

- Corrected strings are present in the extracted package, including `index.json`, `archive.html`, and related page/static artifacts.

## Bodhi Asset

Compared:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/assets/BodhiCircuitLeaf.png`
- `/tmp/flagfix_069_netlify_package_extract/assets/BodhiCircuitLeaf.png`

SHA256 result:

```text
92437a1aba75f9b6fb0d16f8598e1b0902a08c6c513d9014ac295d29848e49c7  /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/assets/BodhiCircuitLeaf.png
92437a1aba75f9b6fb0d16f8598e1b0902a08c6c513d9014ac295d29848e49c7  /tmp/flagfix_069_netlify_package_extract/assets/BodhiCircuitLeaf.png
```

File result:

```text
/tmp/flagfix_069_netlify_package_extract/assets/BodhiCircuitLeaf.png: PNG image data, 2048 x 2048, 8-bit/color RGBA, non-interlaced
```

Result:

- Bodhi asset hash matches the approved published source.
- Extracted asset is the approved transparent RGBA PNG.

## Readiness Recommendation

Recommendation: package is READY for manual Netlify upload decision.

The package passed:

- SHA256 verification;
- extraction test;
- extracted file count check;
- source vs extracted parity check;
- key file existence checks;
- stale/corrected string checks;
- Bodhi asset hash/file checks.

Any actual Netlify upload/deployment should still be a separate explicit operator-approved sprint.

## Explicit Non-Actions

- No deploy.
- No Netlify upload.
- No push.
- No build or pipeline run.
- No DeepL call.
- No translation.
- No CSL modification.
- No metadata CSV modification.
- No `Translation_Control_Center.csv` modification.
- No SP10/SP11 modification.
- No sync/copy into any repo.
- No `.gitignore` change.
- No `axis-niddhi-published` modification.
- No production static modification.
