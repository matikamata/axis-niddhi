# PureDhamma Canon — Release V1

**Tag:**     `puredhamma-v1`  
**Engine:**  AXIS-NIDDHI V5.4  
**Corpus:**  PureDhamma — Teachings of Professor Lal  
**Tagged:**  2026-03-13T00:21:17Z  

---

## Canon Summary

| Field | Value |
|-------|-------|
| Posts | 748 |
| Translations (PT-BR) | 93 |
| Source | PureDhamma-backup_2025-12-31-T100216Z.zip |
| Canon hash | `b71071f92b9731dbcbe552d23d3b8b9e...` |
| Reproducible | ✅ Yes |

---

## What this is

PureDhamma Canon V1 is the first formally sealed release of the
PureDhamma teachings archive, compiled by the AXIS-NIDDHI Canon Compilation Engine.

The canon contains 748 posts in English with 93 posts translated into
Portuguese (PT-BR), extracted from the original WordPress backup dated
2025-12-31.

---

## Cryptographic integrity

```bash
# Verify canon integrity
python3 scripts/core/SA05_verify_canon_integrity.py

# Expected output:
# ✅ CANON VERIFIED
```

Verify canon hash manually:
```bash
python3 -c "
import json
s = json.load(open('build_seal.json'))
print('Engine  :', s['engine'], 'V'+s['engine_version'])
print('Entries :', s['entries'])
print('Hash    :', s['canon_hash'][:32]+'...')
print('Sealed  :', s['reproducible'])
"
```

---

## Rebuild from source

A Steward holding the source ZIP can reproduce this exact canon:

```bash
# With source ZIP: PureDhamma-backup_2025-12-31-T100216Z.zip
bash scripts/core/run_full_pipeline.sh --full
python3 scripts/core/SA05_verify_canon_integrity.py
```

The build is deterministic. Given the same source ZIP and pipeline,
the canon hash will match.

---

## Files in this tag

| File | Purpose |
|------|---------|
| `canon_manifest.json` | Cryptographic manifest of all canon components |
| `build_seal.json` | Reproducible build declaration |
| `README_release.md` | This file |
