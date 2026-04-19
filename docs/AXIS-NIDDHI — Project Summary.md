> Question to Claude Sonnet 4.6 (inside Antigravity.Google):

- Sanity check - can you please summarize the project in this folder?

Let me dig deeper into the key files to understand the project properly.

Viewed README_HUMANS.md:1-132
Viewed AXIS_PROTOCOL.md:1-225
Viewed capsule_manifest.json:1-27
Listed directory core
Listed directory 13-ssg
Listed directory 09-csl
Listed directory release
Listed directory mirror

Now I have a thorough picture. Here's the full summary:

---

## AXIS-NIDDHI — Project Summary

This is a **deterministic content preservation and translation pipeline** for the Buddhist teaching corpus originally published at **PureDhamma.net** by Lal A. — a scientific interpretation of the Buddha's Pāli Canon teaching.

---

### 🎯 Mission

Preserve, translate, and distribute **748 posts** covering the full scope of Buddha Dhamma (ethics, Abhidhamma, dependent origination, meditation, path to Nibbāna) so that the teaching is **never lost**.

---

### 🏗️ Architecture — 4 Pipeline Stages

```
SOURCE ZIP (PureDhamma backup, ~2.3 GB)
    │
    ▼  [SG] EXTRACTION
    │   Extract HTML → Clean → Build CSL → Harvest assets
    │
    ▼  [SP] PROCESSING
    │   Migrate pt-BR stubs → Upgrade identities → Translate via DeepL
    │   Compile glossary (986 terms) → Fix headers → Convert audio
    │
    ▼  [SA] AUDIT
    │   Final audit → Freeze translations → Generate cryptographic manifests
    │   Verify integrity → Generate build seal (reproducibility guarantee)
    │
    ▼  [SD] DEPLOYMENT
        Generate asset/slug maps → Build static site (748 bilingual HTML pages)
```

---

### 📦 Key Components

| Directory | Purpose |
|---|---|
| `sources/` | Original PureDhamma backup ZIP (~2.3 GB) |
| `09-csl/` | **Canon Source Library** — 748+ canonical entries, each with `identity.json`, `en-US/content.html`, `pt-BR/content.html`, and assets |
| `03-translations/` | Translation working folders organized by PDPN code (93 batches) |
| `13-ssg/` | Static site generator (Python `build.py` + templates) |
| `13-static-site/` | **Output** — 748 bilingual HTML pages, fully offline-readable |
| `scripts/core/` | 38 pipeline scripts (SG/SP/SA/SD stages + utilities) |
| `metadata/` | Control center CSVs, glossary config, slug map, translation status |
| `capsule/` | **Time Capsule** — sealed, self-describing archive with cryptographic integrity hashes, a concept/semantic layer, learning paths navigator, and a P2P mirror protocol |
| `ledger/` | Append-only canon registry |
| `release/` | Sealed release snapshot with SHA-256 manifest |
| `mirror/` | P2P distribution endpoint |

---

### 🔐 Integrity Model

The entire pipeline is **fully reproducible** from the source ZIP. Every artefact is SHA-256 hashed at 7 levels: `canon_hash → csl_hash → translations_hash → site_build_hash → pipeline_hash → manifest_hash → seed_integrity_hash`.

---

### 🌐 Output & Distribution

- **Static bilingual site** (en-US + pt-BR) serveable offline
- **Capsule** for long-term archival (sealed 2026-03-13)
- **P2P mirror protocol** for distributing seeds to other AXIS nodes
- **Packages**: `sojourner` (~33 MB lightweight) and `steward` (full)

---

**In one sentence:** This is a hermetically sealed, cryptographically verified pipeline that took a WordPress backup of a Buddhist teaching website, translated it to Portuguese via DeepL, and produced an offline-readable bilingual static site — designed to survive the internet.
