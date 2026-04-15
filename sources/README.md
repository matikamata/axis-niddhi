# Source Corpus

This directory holds the canonical WordPress backup ZIP that AXIS-NIDDHI processes.

**The file is not included in this repository.**

---

## Why

The content belongs to **Lal A.** at [PureDhamma.net](https://puredhamma.net). It is his life's work. It is not ours to distribute.

AXIS-NIDDHI is the engine. The teaching is his.

---

## How to Obtain It

Contact Prof Lal A. at PureDhamma.net directly and explain your purpose. He will assess whether to provide the backup.

If you are a **Kalyāṇamitta** (a validated language contributor — see [`CONTRIBUTING.md`](../CONTRIBUTING.md)), note this in your request.

---

## Expected File

Once you have the file, place it here:

```
sources/
└── PureDhamma-backup_YYYY-MM-DD-THHMMSSZ.zip     (~2.3 GB)
```

Then verify it:

```bash
axis integrity
```

The `canon_hash` in the pipeline manifest is a SHA-256 of this ZIP. Any bit-level change produces a different hash — and a different (non-canonical) corpus.

---

## A Note on Reproducibility

The `seed_integrity_hash` recorded in `pipeline/capsule/seeds/puredhamma-v1/seed_manifest.json` was computed against the **specific ZIP file for which this engine was built** (backup dated 2025-12-31).

If you obtain a later backup, the corpus will differ — new essays, updated content — and you will be producing a new canon version, not reproducing the existing one. Both are valid; they are different.

Register new canon versions via:

```bash
axis ledger add <corpus-name> <version-tag>
```
